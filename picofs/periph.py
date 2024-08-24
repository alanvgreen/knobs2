from rp2 import DMA
from uctypes import addressof
from machine import mem32


class PeripheralRegisters:
    """An APB Peripheral"""
    def __init__(self, base_address):
        self._base = base_address

    def get(self, idx):
        return mem32[self._base + idx]

    def set(self, idx, value):
        mem32[self._base + idx] = value

    def btoggle(self, idx, mask):
        mem32[self._base + idx + 0x1000] = mask

    def bset(self, idx, mask):
        mem32[self._base + idx + 0x2000] = mask
    
    def bclr(self, idx, mask):
        mem32[self._base + idx + 0x3000] = mask


ADC_BASE = 0x4004c000

ADC_CS     = 0x0
ADC_RESULT = 0x4
ADC_FCS    = 0x8
ADC_FIFO   = 0xc


class ADCRegisters(PeripheralRegisters):
    def __init__(self):
        return super().__init__(ADC_BASE)

    @property
    def cs(self):
        return self.get(ADC_CS)

    @property
    def fcs(self):
        return self.get(ADC_FCS)

    def prepare(self):
        self.stop()
        # ensure ADC 1 is selected
        self.bclr(ADC_CS, 7 << 17)
        self.bset(ADC_CS, 1 << 17)

        # Set threshold, dreq_en and en as recommended
        thresh = 1 << 24
        dreq_en = 1 << 3
        en = 1 << 0
        self.set(ADC_FCS, thresh | dreq_en | en)

    def start(self):
        start_many = 1 << 3
        self.bset(ADC_CS, start_many)

    def stop(self):
        # Stop
        start_many = 1 << 3
        self.bclr(ADC_CS, start_many)

        # Drain any existing fifo
        empty = 1 << 8
        while not (self.get(ADC_FCS) & empty):
            self.get(ADC_FIFO)

    def get_fifo_addr(self):
        return self._base + ADC_FIFO


"""
The RP2040 DMA (Section 2.5) can fetch ADC samples from the sample FIFO, by performing a normal memory-mapped
read on the FIFO register, paced by the ADC_DREQ system data request signal. The following must be considered:
    • The sample FIFO must be enabled (FCS.EN) so that samples are written to it; the FIFO is disabled by default so
    that it does not inadvertently fill when the ADC is used for one-shot conversions.
    • The ADC’s data request handshake (DREQ) must be enabled, via FCS.DREQ_EN.
    • The DMA channel used for the transfer must select the DREQ_ADC data request signal (Section 2.5.3.1).
    • The threshold for DREQ assertion (FCS.THRESH) should be set to 1, so that the DMA transfers as soon as a single
    sample is present in the FIFO. Note this is also the threshold used for IRQ assertion, so non-DMA use cases might
    prefer a higher value for less frequent interrupts.
    • If the DMA transfer size is set to 8 bits, so that the DMA transfers to a byte array in memory, FCS.SHIFT must also
    be set, to pre-shift the FIFO samples to 8 bits of significance.
    • If multiple input channels are to be sampled, CS.RROBIN contains a 5-bit mask of those channels (4 external inputs
    plus temperature sensor). Additionally CS.AINSEL must select the channel for the first sample.
    • The ADC sample rate (Section 4.9.2.2) should be configured before starting the ADC.
    Once the ADC is suitably configured, the DMA channel should be started first, and the ADC conversion should be started
    second, via CS.START_MANY. Once the DMA completes, the ADC can be halted, or a new DMA transfer promptly
    started. After clearing CS.START_MANY to halt the ADC, software should also poll CS.READY to make sure the last
    conversion has finished, and then drain any stray samples from the FIFO
"""

from __future__ import annotations

GAN_WUXING = {
    "\u7532": "\u6728",
    "\u4e59": "\u6728",
    "\u4e19": "\u706b",
    "\u4e01": "\u706b",
    "\u620a": "\u571f",
    "\u5df1": "\u571f",
    "\u5e9a": "\u91d1",
    "\u8f9b": "\u91d1",
    "\u58ec": "\u6c34",
    "\u7678": "\u6c34",
}

ZHI_WUXING = {
    "\u5b50": "\u6c34",
    "\u4e11": "\u571f",
    "\u5bc5": "\u6728",
    "\u536f": "\u6728",
    "\u8fb0": "\u571f",
    "\u5df3": "\u706b",
    "\u5348": "\u706b",
    "\u672a": "\u571f",
    "\u7533": "\u91d1",
    "\u9149": "\u91d1",
    "\u620c": "\u571f",
    "\u4ea5": "\u6c34",
}


def gan_wuxing(gan: str) -> str:
    return GAN_WUXING.get(gan, "")


def zhi_wuxing(zhi: str) -> str:
    return ZHI_WUXING.get(zhi, "")

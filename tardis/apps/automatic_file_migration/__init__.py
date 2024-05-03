"""This app provides tools to automatically manage file migration through different tiers
of storage.

The module is RO-Crate aware and will migrate metadata files to a separate storage location
than the files. This allows for mutability/immutability policies to be applied appropriately
at the bucket level.

..moduleauthor:: Chris Seal <c.seal@auckland.ac.nz>"""

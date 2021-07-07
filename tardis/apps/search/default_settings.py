'''
Default settings for search app
'''

SUSPEND_ES_SIGNALS = False
'''
Determine whether or not to auto-index objects using a post-save trigger:
allows for automatic creation/deletion of indexes when objects are created/deleted,
but may run into networking issues as the post-save hooks are not async'ed.
'''

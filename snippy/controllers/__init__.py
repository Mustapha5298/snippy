"""
## 𓉴 Controllers
This folder contains the `traffic cops` 🚦 of Snippy.
----

### Responsible for:
- Validating command inputs and parameters
- Making sure functions receive the correct data
- Directing execution flow to the right logic

----
`🍏 This can stop you for number of scrapes per day.`
"""

from .control_openlibrary import OpenLibraryController
from .control_precaution import PrecautionController

__all__ = [
    "PrecautionController", "OpenLibraryController"
]
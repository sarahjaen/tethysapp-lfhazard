from tethys_sdk.base import TethysAppBase


class Lfhazard(TethysAppBase):
    """
    Tethys app class for Liquefaction Hazard Lookup.
    """

    name = 'Liquefaction Hazard Parameter Lookup'
    index = 'home'
    icon = 'lfhazard/images/icon.gif'
    package = 'lfhazard'
    root_url = 'lfhazard'
    color = '#915F6D'
    description = ''
    tags = ''
    enable_feedback = False
    feedback_emails = []

from tethys_sdk.base import TethysAppBase
from tethys_sdk.app_settings import CustomSetting


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

    def custom_settings(self):
        return (
            CustomSetting(
                name='data_path',
                type=CustomSetting.TYPE_STRING,
                description='Server path to the directory of CSV data',
                required=True,
            ),
        )

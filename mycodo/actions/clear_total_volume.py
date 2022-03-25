# coding=utf-8
import threading

from flask_babel import lazy_gettext

from mycodo.databases.models import Actions
from mycodo.databases.models import Input
from mycodo.actions.base_action import AbstractFunctionAction
from mycodo.utils.database import db_retrieve_table_daemon

ACTION_INFORMATION = {
    'name_unique': 'clear_total_volume',
    'name': f"{lazy_gettext('Flow Meter')}: {lazy_gettext('Clear Total Volume')}",
    'library': None,
    'manufacturer': 'Mycodo',
    'application': ['functions'],

    'url_manufacturer': None,
    'url_datasheet': None,
    'url_product_purchase': None,
    'url_additional': None,

    'message': 'Clear the total volume saved for a flow meter Input. The Input must have the Clear Total Volume option.',

    'usage': 'Executing <strong>self.run_action("{ACTION_ID}")</strong> will clear the total volume for the selected flow meter Input. '
             'Executing <strong>self.run_action("{ACTION_ID}", value={"input_id": "959019d1-c1fa-41fe-a554-7be3366a9c5b"})</strong> will clear the total volume for the flow meter Input with the specified ID.',

    'custom_options': [
        {
            'id': 'controller',
            'type': 'select_device',
            'default_value': '',
            'options_select': [
                'Input'
            ],
            'name': lazy_gettext('Controller'),
            'phrase': 'Select the flow meter Input'
        }
    ]
}


class ActionModule(AbstractFunctionAction):
    """Function Action: Clear Total Volume."""
    def __init__(self, action_dev, testing=False):
        super().__init__(action_dev, testing=testing, name=__name__)

        self.controller_id = None

        action = db_retrieve_table_daemon(
            Actions, unique_id=self.unique_id)
        self.setup_custom_options(
            ACTION_INFORMATION['custom_options'], action)

        if not testing:
            self.try_initialize()

    def initialize(self):
        self.action_setup = True

    def run_action(self, message, dict_vars):
        try:
            controller_id = dict_vars["value"]["input_id"]
        except:
            controller_id = self.controller_id

        this_input = db_retrieve_table_daemon(
            Input, unique_id=controller_id, entry='first')

        if not this_input:
            msg = f" Error: Input with ID '{controller_id}' not found."
            message += msg
            self.logger.error(msg)
            return message

        message += f" Clear total volume of Input {controller_id} ({this_input.name})."
        clear_volume = threading.Thread(
            target=self.control.custom_button,
            args=("Input", this_input.unique_id, "clear_total_volume", {},))
        clear_volume.start()

        self.logger.debug(f"Message: {message}")

        return message

    def is_setup(self):
        return self.action_setup
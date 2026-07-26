import keyboard_controller
import mouse_controller


def parse_action(action):
    if not isinstance(action, str) or not action.strip():
        raise ValueError("Action must be a non-empty string")

    action_name = action.strip()

    if keyboard_controller.is_valid_key(action_name):
        return "keyboard", action_name

    if mouse_controller.is_valid_button(action_name):
        return "mouse", action_name.lower()

    raise ValueError("Unsupported keyboard key, combination, or mouse action: " + action_name)


def execute_action(action):
    action_type, action_name = parse_action(action)

    if action_type == "keyboard":
        keyboard_controller.press_and_release(action_name)
        return

    mouse_controller.click_button(action_name)

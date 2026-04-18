import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from rich.console import Console
from rich.panel import Panel

load_dotenv()

app = Flask(__name__)
CORS(app)

console = Console()
PORT = int(os.getenv("PORT", "3006"))
bulb_state = {
    "status": False,
    "brightness": 100,
    "rgb": {"r": 255, "g": 255, "b": 255},
}


def parse_status(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"on", "true", "1", "yes", "active"}:
            return True
        if normalized in {"off", "false", "0", "no", "inactive"}:
            return False
    return None


def parse_brightness(value):
    if isinstance(value, bool):
        return None

    if isinstance(value, (int, float)):
        brightness = int(value)
    elif isinstance(value, str):
        raw = value.strip()
        if raw == "":
            return None
        try:
            brightness = int(float(raw))
        except ValueError:
            return None
    else:
        return None

    if 0 <= brightness <= 100:
        return brightness
    return None


def parse_rgb(value):
    if isinstance(value, str):
        raw = value.strip()
        if raw.startswith("#") and len(raw) == 7:
            try:
                return {
                    "r": int(raw[1:3], 16),
                    "g": int(raw[3:5], 16),
                    "b": int(raw[5:7], 16),
                }
            except ValueError:
                return None

        parts = [item.strip() for item in raw.split(",")]
        if len(parts) == 3:
            value = parts

    if isinstance(value, (list, tuple)) and len(value) == 3:
        channels = (value[0], value[1], value[2])
    elif isinstance(value, dict):
        if all(key in value for key in ("r", "g", "b")):
            channels = (value.get("r"), value.get("g"), value.get("b"))
        elif all(key in value for key in ("red", "green", "blue")):
            channels = (value.get("red"), value.get("green"), value.get("blue"))
        else:
            return None
    else:
        return None

    parsed = []
    for channel in channels:
        if isinstance(channel, bool):
            return None
        try:
            numeric = int(channel)
        except (TypeError, ValueError):
            return None
        if not 0 <= numeric <= 255:
            return None
        parsed.append(numeric)

    return {"r": parsed[0], "g": parsed[1], "b": parsed[2]}


def status_to_text(value):
    if value is True:
        return "on"
    if value is False:
        return "off"
    return "unknown"


def rgb_to_hex(rgb):
    return "#{:02X}{:02X}{:02X}".format(rgb["r"], rgb["g"], rgb["b"])


def bulb_response_payload():
    rgb = bulb_state["rgb"]
    return {
        "status": status_to_text(bulb_state["status"]),
        "brightness": bulb_state["brightness"],
        "rgb": rgb,
        "hex": rgb_to_hex(rgb),
    }


@app.post("/bulb/status")
def set_bulb_status():
    raw_payload = request.get_json(silent=True)
    if raw_payload is None or not isinstance(raw_payload, dict):
        return jsonify({"error": "JSON object payload required"}), 400

    payload = raw_payload
    has_updates = False

    if "status" in payload:
        parsed_status = parse_status(payload.get("status"))
        if parsed_status is None:
            return jsonify({"error": "status must be one of on/off/true/false/1/0"}), 400
        bulb_state["status"] = parsed_status
        has_updates = True

    brightness_provided = "brightness" in payload or "brighteness" in payload
    if brightness_provided:
        brightness_value = payload.get("brightness", payload.get("brighteness"))
        parsed_brightness = parse_brightness(brightness_value)
        if parsed_brightness is None:
            return jsonify({"error": "brightness must be an integer from 0 to 100"}), 400
        bulb_state["brightness"] = parsed_brightness
        has_updates = True

    if "rgb" in payload:
        parsed_rgb = parse_rgb(payload.get("rgb"))
        if parsed_rgb is None:
            return jsonify(
                {
                    "error": "rgb must be #RRGGBB, 'r,g,b', [r,g,b], or an object with r/g/b in range 0-255"
                }
            ), 400
        bulb_state["rgb"] = parsed_rgb
        has_updates = True

    if not has_updates:
        return jsonify({"error": "provide at least one of: status, brightness/brighteness, rgb"}), 400

    state_payload = bulb_response_payload()
    rgb = state_payload["rgb"]

    console.print(
        Panel(
            f"[bold]Device:[/] bulb\n"
            f"[bold]Status:[/] {state_payload['status']}\n"
            f"[bold]Brightness:[/] {state_payload['brightness']}%\n"
            f"[bold]RGB:[/] {rgb['r']}, {rgb['g']}, {rgb['b']} ({state_payload['hex']})",
            title="Bulb Status Updated",
            border_style="green",
        )
    )

    return jsonify(state_payload), 200


@app.get("/bulb/status")
def get_bulb_status():
    return jsonify(bulb_response_payload()), 200


@app.errorhandler(Exception)
def handle_error(err):
    console.print(Panel(f"[bold red]Error handling request:[/] {err}", border_style="red"))
    return jsonify({"status": "error"}), 500


if __name__ == "__main__":
    console.clear()
    console.print(
        Panel(
            f"[bold cyan]Cloud Simulation Backend[/bold cyan]\nListening on [green]http://localhost:{PORT}[/green]",
            border_style="cyan",
        )
    )
    console.print(f"[dim]Waiting for IoT telemetry on port[/dim] [bold green]{PORT}[/bold green]")
    app.run(host="0.0.0.0", port=PORT, debug=False)
# Cloud Simulation Bulb API

## Base URL

- Local: `http://172.16.48.184:3001`
- Port comes from `PORT` env var (default `3001`).

## Content Type

All request bodies should be JSON:

- `Content-Type: application/json`

## Bulb State Model

Successful bulb responses return this shape:

```json
{
  "status": "on",
  "brightness": 80,
  "rgb": {
    "r": 255,
    "g": 180,
    "b": 40
  },
  "hex": "#FFB428"
}
```

Field details:

- `status`: `on` or `off`
- `brightness`: integer from `0` to `100`
- `rgb.r`, `rgb.g`, `rgb.b`: integers from `0` to `255`
- `hex`: computed color in `#RRGGBB`

## Endpoints

### GET /bulb/status

Returns current bulb state.

#### Success Response: 200

```json
{
  "status": "off",
  "brightness": 100,
  "rgb": {
    "r": 255,
    "g": 255,
    "b": 255
  },
  "hex": "#FFFFFF"
}
```

### POST /bulb/status

Updates bulb state. Partial updates are supported (send one or more fields).

#### Accepted input fields

- `status`
- `brightness` (alias also supported: `brighteness`)
- `rgb`

#### `status` accepted values

- String: `on`, `off`, `true`, `false`, `1`, `0`, `yes`, `no`, `active`, `inactive`
- Boolean: `true`, `false`
- Number: non-zero = `on`, zero = `off`

#### `brightness` accepted values

- Integer in range `0` to `100`
- Numeric strings are accepted if they can be converted to integer

#### `rgb` accepted formats

1. Hex string: `"#RRGGBB"`
2. CSV string: `"r,g,b"`
3. Array: `[r, g, b]`
4. Object with channels:
   - `{ "r": 10, "g": 200, "b": 90 }`
   - `{ "red": 10, "green": 200, "blue": 90 }`

All RGB channels must be `0` to `255`.

#### Success Response: 200

Returns full bulb state after update.

```json
{
  "status": "on",
  "brightness": 35,
  "rgb": {
    "r": 51,
    "g": 170,
    "b": 255
  },
  "hex": "#33AAFF"
}
```

#### Error Responses: 400

Examples:

```json
{ "error": "JSON object payload required" }
```

```json
{ "error": "status must be one of on/off/true/false/1/0" }
```

```json
{ "error": "brightness must be an integer from 0 to 100" }
```

```json
{
  "error": "rgb must be #RRGGBB, 'r,g,b', [r,g,b], or an object with r/g/b in range 0-255"
}
```

```json
{ "error": "provide at least one of: status, brightness/brighteness, rgb" }
```

## Quick Examples

### Turn bulb on + set brightness + color

```bash
curl -X POST http://172.16.48.184:3001/bulb/status \
  -H "Content-Type: application/json" \
  -d "{\"status\":\"on\",\"brightness\":80,\"rgb\":{\"r\":255,\"g\":180,\"b\":40}}"
```

### Brightness only

```bash
curl -X POST http://172.16.48.184:3001/bulb/status \
  -H "Content-Type: application/json" \
  -d "{\"brightness\":25}"
```

### RGB using hex

```bash
curl -X POST http://172.16.48.184:3001/bulb/status \
  -H "Content-Type: application/json" \
  -d "{\"rgb\":\"#33AAFF\"}"
```

### Read state

```bash
curl http://172.16.48.184:3001/bulb/status
```

## Generic Server Error

Unexpected failures return:

```json
{ "status": "error" }
```

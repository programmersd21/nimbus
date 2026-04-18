# Nimbus — Dynamic Island for Windows

A physics-animated **Dynamic Island** clone for Windows with real system integrations. Nimbus brings the elegant notification and status display from macOS to your Windows desktop with smooth spring animations, live media controls, system notifications, and more.

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-Beta-yellow)

## Features

- 🎬 **Physics-Based Animations** — Spring physics engine for fluid, natural-feeling animations
- 📱 **Dynamic Island UI** — Floating notification panel with smooth expand/collapse behavior
- 🎵 **Media Control Integration** — Display and control media playback from any application
- 🔔 **System Notifications** — Elegant notification handling and display
- 🕐 **Real-Time System Info** — Clock, timer, and system status monitoring
- ⚙️ **Windows Integration** — Uses Windows Runtime APIs for deep system integration
- 🎨 **Custom Font Support** — Professional appearance with bundled typography
- 🖥️ **System Tray Support** — Minimize to tray for unobtrusive operation

## Requirements

- **Windows 10+** (Windows 11 recommended)
- **Python 3.10+**
- **pip** or **conda** package manager

## Installation

### Quick Install

```bash
pip install -e .
```

### Development Install

For development with testing and linting tools:

```bash
pip install -e ".[dev]"
```

Or use the Makefile:

```bash
make dev
```

## Usage

### Run the Application

```bash
nimbus
```

Or using Python:

```bash
python -m nimbus
```

Or using the Makefile:

```bash
make run
```

## Development

### Project Structure

```
nimbus/
├── nimbus/
│   ├── __main__.py          # Application entry point
│   ├── app.py               # Qt application lifecycle
│   ├── window.py            # Main window implementation
│   ├── state.py             # Global application state
│   ├── input.py             # Input handling
│   ├── layout.py            # UI layout system
│   ├── renderer.py          # Rendering pipeline
│   ├── tray.py              # System tray integration
│   │
│   ├── core/                # Core animation system
│   │   ├── animation.py     # Animation framework
│   │   └── state.py         # Core state management
│   │
│   ├── modules/             # Feature modules
│   │   ├── clock.py         # Time display
│   │   ├── media.py         # Media playback control
│   │   ├── notifications.py # Notification system
│   │   ├── status.py        # System status display
│   │   ├── timer.py         # Timer functionality
│   │   └── permissions.py   # Permission management
│   │
│   ├── utils/               # Utility functions
│   │   └── config.py        # Configuration management
│   │
│   └── animation/           # Animation utilities
│
├── tests/                   # Test suite
│   ├── test_modules.py      # Module tests
│   ├── test_spring.py       # Animation physics tests
│   └── test_state.py        # State management tests
│
├── assets/                  # Application assets
│   ├── fonts/               # Custom typefaces
│   └── icons/               # Application icons
│
├── pyproject.toml           # Project configuration
├── requirements.txt         # Runtime dependencies
└── Makefile                 # Development commands
```

### Development Commands

Use the Makefile for common development tasks:

```bash
# Install development dependencies
make dev

# Run the application
make run

# Lint code
make lint

# Format code
make format

# Type checking
make typecheck

# Run tests
make test

# Build distribution package
make build

# Clean build artifacts
make clean

# Show all available commands
make help
```

### Running Tests

```bash
pytest
pytest -v                    # Verbose output
pytest tests/test_modules.py # Run specific test file
```

### Code Quality

The project uses:

- **ruff** — Fast Python linter and formatter
- **mypy** — Static type checker
- **pytest** — Test framework
- **pytest-qt** — Qt testing utilities

Run all checks:

```bash
make lint && make typecheck && make test
```

## Architecture

### Display States

The pill cycles through multiple UI states, each with tailored content:

- **Idle** — Compact clock display (126×34 px)
- **Media** — Now playing info with visualizer bars
- **Notification** — Latest notification with scrolling title & body
- **Stats (CPU/RAM/SSD)** — System resource gauges
- **Privacy** — Camera & microphone access indicators
- **Expanded** — Full dashboard with time + media info
- **Big Stats** — System resources with detailed graphs

**Display Cycle:** IDLE → MEDIA → NOTIFICATION → STATS_CPU → STATS_RAM → STATS_PRIVACY (6 seconds per state)

### Animation System

Nimbus features a physics-based animation engine using **spring dynamics** for natural, responsive animations:

- Smooth easing between states with configurable spring presets
- Configurable spring stiffness and damping per state
- Frame-rate independent animations with delta-time stepping
- Hardware-accelerated rendering via Qt
- Scrolling text animation for titles that exceed display width

### UI Features

- **Scrolling Text** — Long titles automatically scroll horizontally when content exceeds container width
- **Responsive Sizing** — Pill dynamically resizes and reshapes for each state
- **Interactive Hover** — Hover over pill to make it interactive; click to expand
- **Auto-Collapse** — Expanded states automatically return to idle after 3 seconds

### Module System

Feature functionality is organized into independent modules:

- **ClockModule** — Displays current time
- **MediaModule** — Integrates with Windows Media Control APIs
- **NotificationModule** — Manages system notifications with queueing
- **StatusModule** — Shows system information (CPU, RAM, SSD)
- **TimerModule** — Countdown/timer functionality
- **PermissionModule** — Handles system permissions (camera, microphone)

### State Management

- Centralized application state in `core/state.py`
- Reactive state updates trigger UI re-renders
- Type-safe state transitions with spring animation presets
- Spring physics drives smooth geometry transitions

## Dependencies

### Runtime

- **PySide6** — Qt6 Python bindings for UI
- **psutil** — System and process utilities
- **Pillow** — Image processing
- **numpy** — Numerical computations (for animation)
- **pywin32** — Windows API access
- **winrt** — Windows Runtime APIs (media control, permissions)

### Development

- **pytest** — Test framework
- **pytest-qt** — Qt test utilities
- **ruff** — Linter and formatter
- **mypy** — Type checker

## Configuration

Configuration is managed through `nimbus/utils/config.py`. Customize:

- Window behavior
- Animation parameters
- Notification display duration
- Module preferences

## Troubleshooting

### Application won't start

1. Verify Python version: `python --version` (should be 3.10+)
2. Check dependencies: `pip list | grep PySide6`
3. Check font file exists: `./assets/fonts/font.ttf`
4. Review logs for errors

### Media control not working

- Ensure media player app (Spotify, iTunes, etc.) is running
- Check Windows 11 Settings → Privacy & Security → App Permissions → Media player control
- Verify `winrt-Windows.Media.Control` is installed

### Animation stuttering

- Close resource-heavy applications
- Update graphics drivers
- Check system resource usage: `tasklist` or Task Manager

## License

Nimbus is released under the **MIT License**. See [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Credits

Built with [PySide6](https://wiki.qt.io/Qt_for_Python), inspired by Apple's Dynamic Island.

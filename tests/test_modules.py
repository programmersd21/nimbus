"""
tests/test_modules.py — Module Tests
"""

from nimbus.modules import (
    ClockModule,
    MediaModule,
    Notification,
    NotificationModule,
    StatusModule,
    TimerModule,
)


class TestClockModule:
    """Clock module tests."""

    def test_clock_initialization(self) -> None:
        """Test clock initialization."""
        clock = ClockModule()
        assert clock.get_hour() in range(24)
        assert clock.get_minute() in range(60)
        assert clock.get_second() in range(60)

    def test_clock_formatters(self) -> None:
        """Test time formatters."""
        clock = ClockModule()
        time_str = clock.get_time()
        assert ":" in time_str

        time_with_sec = clock.get_time_with_seconds()
        assert time_with_sec.count(":") == 2


class TestMediaModule:
    """Media module tests."""

    def test_media_initialization(self) -> None:
        """Test media initialization."""
        media = MediaModule()
        assert media.is_playing()
        assert media.get_title()
        assert media.get_artist()

    def test_media_playback_control(self) -> None:
        """Test playback controls."""
        media = MediaModule()
        media.toggle_play()
        assert not media.is_playing()
        media.toggle_play()
        assert media.is_playing()

    def test_media_track_navigation(self) -> None:
        """Test track navigation."""
        media = MediaModule()
        initial_title = media.get_title()
        media.next_track()
        assert media.get_title() != initial_title

    def test_media_visualizer(self) -> None:
        """Test visualizer bars."""
        media = MediaModule()
        bars = media.get_bar_heights()
        assert len(bars) == 5
        assert all(3.0 <= h <= 18.0 for h in bars)


class TestNotificationModule:
    """Notification module tests."""

    def test_notification_creation(self) -> None:
        """Test notification creation."""
        notif = Notification(title="Test", body="Test notification")
        assert notif.title == "Test"
        assert notif.body == "Test notification"
        assert not notif.is_expired()

    def test_notification_queue(self) -> None:
        """Test notification queue."""
        notif_module = NotificationModule()
        assert notif_module.get_queue_size() == 0

        notif = Notification(title="Test", body="Body")
        notif_module.add_notification(notif)
        assert notif_module.get_queue_size() == 1
        assert notif_module.get_current() == notif


class TestTimerModule:
    """Timer module tests."""

    def test_timer_initialization(self) -> None:
        """Test timer initialization."""
        timer = TimerModule()
        assert not timer.is_running()
        assert timer.get_remaining_sec() == 0

    def test_timer_start_stop(self) -> None:
        """Test timer start/stop."""
        timer = TimerModule()
        timer.start(60)
        assert timer.is_running()
        assert timer.get_remaining_sec() == 60

        timer.stop()
        assert not timer.is_running()
        assert timer.get_remaining_sec() == 0

    def test_timer_progress(self) -> None:
        """Test timer progress."""
        timer = TimerModule()
        timer.start(100)
        progress = timer.get_progress()
        assert 0.0 <= progress <= 1.0


class TestStatusModule:
    """Status module tests."""

    def test_status_initialization(self) -> None:
        """Test status module initialization."""
        status = StatusModule()
        assert status.get_cpu_percent() >= 0.0
        assert status.get_memory_percent() >= 0.0

    def test_network_status(self) -> None:
        """Test network status."""
        status = StatusModule()
        net = status.get_network_status()
        assert isinstance(net.is_connected, bool)
        assert 0 <= net.signal_strength <= 100

    def test_camera_microphone_status(self) -> None:
        """Test camera/mic status."""
        status = StatusModule()
        # These should return False in demo mode
        assert isinstance(status.is_camera_in_use(), bool)
        assert isinstance(status.is_microphone_in_use(), bool)

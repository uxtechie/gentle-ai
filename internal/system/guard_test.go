package system

import (
	"errors"
	"strings"
	"testing"
)

func TestEnsureSupportedOSAllowsMacOS(t *testing.T) {
	if err := EnsureSupportedOS("darwin"); err != nil {
		t.Fatalf("expected no error for macOS, got %v", err)
	}
}

func TestEnsureSupportedOSRejectsOtherPlatforms(t *testing.T) {
	for _, goos := range []string{"linux", "windows", "freebsd"} {
		t.Run(goos, func(t *testing.T) {
			err := EnsureSupportedOS(goos)
			if !errors.Is(err, ErrUnsupportedOS) {
				t.Fatalf("expected ErrUnsupportedOS, got %v", err)
			}
			if !strings.Contains(err.Error(), "only macOS is supported") {
				t.Fatalf("expected macOS-only support message, got %q", err.Error())
			}
			if err := EnsureSupportedPlatform(PlatformProfile{OS: goos, Supported: true}); !errors.Is(err, ErrUnsupportedOS) {
				t.Fatalf("supported profile bypassed OS guard: %v", err)
			}
		})
	}
}

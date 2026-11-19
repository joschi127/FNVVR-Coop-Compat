// New Vegas Co-op by Zyrcxies (https://github.com/Zyrcxies/NewVegasCoop). Reusing this code? See LICENSE: credit and the same license are required.
// Modified in FNVVR-Coop-Compat (https://github.com/joschi127/FNVVR-Coop-Compat): gamepad support for co-op's own
// controls (revive, drag, give a Stimpak) and prompts that name the key or button actually bound.

#pragma once

#include <cstdint>
#include <string>

namespace coop
{
    // The game's gamepad input codes (one per control in its controller bindings, 0xFF when unbound) and the
    // gamepad state it polls each frame. VR mods that feed the game a virtual gamepad land here too.
    constexpr uint8_t kPadUnbound = 0xFF;

    struct PadState
    {
        uint16_t buttons = 0;
        uint8_t leftTrigger = 0, rightTrigger = 0;
        int16_t thumbLX = 0, thumbLY = 0;
    };

    namespace pad
    {
        // XInput button masks
        constexpr uint16_t kDpadUp = 0x0001, kDpadDown = 0x0002, kDpadLeft = 0x0004, kDpadRight = 0x0008,
            kStart = 0x0010, kBack = 0x0020, kLeftThumb = 0x0040, kRightThumb = 0x0080, kLeftShoulder = 0x0100,
            kRightShoulder = 0x0200, kA = 0x1000, kB = 0x2000, kX = 0x4000, kY = 0x8000;
        constexpr uint8_t kTriggerThreshold = 30;     // XINPUT_GAMEPAD_TRIGGER_THRESHOLD
        constexpr int16_t kLeftThumbDeadZone = 7849;  // XINPUT_GAMEPAD_LEFT_THUMB_DEADZONE
    }

    // XInput button mask of a game input code; 0 for triggers, sticks and unknown codes
    inline uint16_t PadButtonMask(uint8_t code)
    {
        switch (code)
        {
        case 0x01: return pad::kDpadUp;
        case 0x02: return pad::kDpadDown;
        case 0x04: return pad::kDpadRight;
        case 0x05: return pad::kDpadLeft;
        case 0x06: return pad::kStart;
        case 0x07: return pad::kBack;
        case 0x08: return pad::kLeftThumb;
        case 0x09: return pad::kRightThumb;
        case 0x0A: return pad::kA;
        case 0x0B: return pad::kB;
        case 0x0C: return pad::kX;
        case 0x0D: return pad::kY;
        case 0x0E: return pad::kRightShoulder;
        case 0x0F: return pad::kLeftShoulder;
        default: return 0;
        }
    }

    // Whether the input with that game code is held in this gamepad state
    inline bool PadInputHeld(uint8_t code, const PadState& state)
    {
        if (uint16_t mask = PadButtonMask(code))
            return (state.buttons & mask) != 0;
        switch (code)
        {
        case 0x10: return state.leftTrigger > pad::kTriggerThreshold;
        case 0x11: return state.rightTrigger > pad::kTriggerThreshold;
        case 0x12: return state.thumbLY > pad::kLeftThumbDeadZone;
        case 0x13: return state.thumbLY < -pad::kLeftThumbDeadZone;
        case 0x14: return state.thumbLX > pad::kLeftThumbDeadZone;
        case 0x15: return state.thumbLX < -pad::kLeftThumbDeadZone;
        default: return false;
        }
    }

    // What a player reads on an Xbox-style gamepad for that game code; nullptr when unbound or unknown
    inline const char* PadInputName(uint8_t code)
    {
        switch (code)
        {
        case 0x01: return "D-pad up";
        case 0x02: return "D-pad down";
        case 0x04: return "D-pad right";
        case 0x05: return "D-pad left";
        case 0x06: return "Start";
        case 0x07: return "Back";
        case 0x08: return "Left stick click";
        case 0x09: return "Right stick click";
        case 0x0A: return "A";
        case 0x0B: return "B";
        case 0x0C: return "X";
        case 0x0D: return "Y";
        case 0x0E: return "RB";
        case 0x0F: return "LB";
        case 0x10: return "LT";
        case 0x11: return "RT";
        default: return nullptr;
        }
    }

    // Whether any input shows on the gamepad (to tell which device the player uses right now)
    inline bool PadActive(const PadState& state)
    {
        return state.buttons != 0 || state.leftTrigger > pad::kTriggerThreshold ||
            state.rightTrigger > pad::kTriggerThreshold || state.thumbLX > pad::kLeftThumbDeadZone ||
            state.thumbLX < -pad::kLeftThumbDeadZone || state.thumbLY > pad::kLeftThumbDeadZone ||
            state.thumbLY < -pad::kLeftThumbDeadZone;
    }

    // Remembers the device last used: the gamepad from its first input, the keyboard or mouse again from theirs
    class InputDevice
    {
    public:
        void Update(bool padActive, bool keyboardOrMouseActive)
        {
            if (keyboardOrMouseActive && !padActive)
                m_gamepad = false;
            else if (padActive && !keyboardOrMouseActive)
                m_gamepad = true;
        }
        bool Gamepad() const { return m_gamepad; }

    private:
        bool m_gamepad = false;
    };

    // The name a prompt shows for a control: the gamepad button while the gamepad is in use and the control has
    // one, otherwise the keyboard (or mouse) name, otherwise the game's default key
    inline std::string ControlPromptName(bool gamepad, uint8_t padCode, const std::string& keyName,
        const char* defaultKey)
    {
        if (gamepad)
            if (const char* name = PadInputName(padCode))
                return name;
        return keyName.empty() ? defaultKey : keyName;
    }
}

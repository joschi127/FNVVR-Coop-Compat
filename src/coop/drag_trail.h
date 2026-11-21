// FNVVR-Coop-Compat (https://github.com/joschi127/FNVVR-Coop-Compat), based on New Vegas Co-op by Zyrcxies
// (https://github.com/Zyrcxies/NewVegasCoop). Licence: see LICENSE (same licence as New Vegas Co-op).

#pragma once

#include <cmath>

namespace coop
{
    // A dragged friend is held at arm's length: they stay where they lie until the dragger has walked further away
    // than an arm's length, then they are pulled along the line between both. The arm's length is `front` while the
    // friend lies in front of the dragger (where they look; people drag walking backwards), `back` behind them, and
    // in between at the sides.
    // Returns whether the friend moves, and where to (toX, toY).
    inline bool DragArmsLength(float friendX, float friendY, float draggerX, float draggerY, float draggerHeading,
        float front, float back, float& toX, float& toY)
    {
        float dx = friendX - draggerX, dy = friendY - draggerY;
        float length = std::sqrt(dx * dx + dy * dy);
        if (length < 1e-3f)
            return false;
        float ux = dx / length, uy = dy / length;
        // Heading 0 looks along +Y, as the game's
        float facing = ux * std::sin(draggerHeading) + uy * std::cos(draggerHeading);
        float reach = (front + back) / 2 + (front - back) / 2 * facing;
        if (length <= reach)
            return false;
        toX = draggerX + reach * ux;
        toY = draggerY + reach * uy;
        return true;
    }
}

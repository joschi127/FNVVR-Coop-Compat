// FNVVR-Coop-Compat (https://github.com/joschi127/FNVVR-Coop-Compat), based on New Vegas Co-op by Zyrcxies
// (https://github.com/Zyrcxies/NewVegasCoop). Licence: see LICENSE (same licence as New Vegas Co-op).

#pragma once

#include <cmath>

namespace coop
{
    // How far the dragger has to walk before the side a dragged friend trails on is taken again, in game units
    constexpr float kDragTrailStep = 8.0f;

    // Keeps (trailX, trailY), a unit vector, pointing back the way the dragger came: from where they were last taken
    // (fromX, fromY) to where they are now (x, y), reversed. Small steps and standing still keep the last direction.
    inline void DragTrail(float& fromX, float& fromY, float x, float y, float& trailX, float& trailY)
    {
        float dx = fromX - x, dy = fromY - y;
        float length = std::sqrt(dx * dx + dy * dy);
        if (length < kDragTrailStep)
            return;
        trailX = dx / length;
        trailY = dy / length;
        fromX = x;
        fromY = y;
    }
}

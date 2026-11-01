-- DORFic window chrome.
--
-- Replaces default/themed/hyprland.lua.tpl entirely (Omarchy skips a template
-- whose output already exists), so the border colors are restated here rather
-- than inherited. Keep them in sync with colors.toml.
--
-- Orange glass: fat rounded corners, a glossy border that runs from white
-- through sunlight gold to orange, a soft ember drop shadow, and strong blur
-- behind every translucent window and shell surface so the wallpaper glows
-- through the tinted panes.

local active_border_color = { colors = { "rgba(ffffffee)", "rgba(ffd23fee)", "rgba(ff8a1fee)" }, angle = 90 }
local inactive_border_color = "rgba(ffb06655)"

hl.config({
  general = {
    gaps_in = 7,
    gaps_out = 14,
    border_size = 3,

    col = {
      active_border = active_border_color,
      inactive_border = inactive_border_color,
    },
  },

  group = {
    col = {
      border_active = active_border_color,
      border_inactive = inactive_border_color,
    },
  },

  decoration = {
    rounding = 18,
    rounding_power = 2.6,

    shadow = {
      enabled = true,
      range = 26,
      render_power = 3,
      offset = "0 8",
      color = "rgba(3a100055)",
      color_inactive = "rgba(3a100030)",
    },

    blur = {
      enabled = true,
      size = 10,
      passes = 3,
      noise = 0.015,
      brightness = 0.95,
      contrast = 1.0,
      vibrancy = 0.35,
      popups = true,
    },
  },
})

-- Glass behind the shell's translucent cards. ignore_alpha keeps the blur to
-- the drawn pixels so the rounded bar capsules don't frost a full-width strip.
hl.layer_rule({
  match = { namespace = "^(omarchy-bar|omarchy-gloss-bar|omarchy-menu|omarchy-notifications|omarchy-osd|omarchy-clipboard|omarchy-emojis|omarchy-polkit|omarchy-reminders)$" },
  blur = true,
  ignore_alpha = 0.2,
})

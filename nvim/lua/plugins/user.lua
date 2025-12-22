-- You can also add or configure plugins by creating files in this `plugins/` folder
-- Here are some examples:

---@type LazySpec
return {
  {
    "goolord/alpha-nvim",
    opts = function(_, opts)
      -- customize the dashboard header
      -- https://manytools.org/hacker-tools/ascii-banner/ for ascii art using ANSI Shadow
      opts.section.header.val = {
        "        ███╗   ██╗███████╗███████╗██╗   ██╗██╗███╗   ███╗       ",
        "        ████╗  ██║██╔════╝██╔══██║██║   ██║██║████╗ ████║       ",
        "        ██╔██╗ ██║█████╗  ██║  ██║██║   ██║██║██╔████╔██║       ",
        "        ██║╚██╗██║██╔══╝  ██║  ██║╚██╗ ██╔╝██║██║╚██╔╝██║       ",
        "        ██║ ╚████║███████╗███████║ ╚████╔╝ ██║██║ ╚═╝ ██║       ",
        "        ╚═╝  ╚═══╝╚══════╝╚══════╝  ╚═══╝  ╚═╝╚═╝     ╚═╝       ",
      }
      return opts
    end,
  },
  {
    "rcarriga/nvim-notify",
    opts = function(_, opts)
      opts.setup = {
        background_colour = "#1e1e2e",
      }
      return opts
    end,
    config = function(_, opts)
      vim.defer_fn(function()
        local notify = require "notify"

        -- Initialize with the settings you defined above
        notify.setup(opts.setup)

        -- Set as default notification provider
        vim.notify = notify

        -- Send the notification now that we are ready
        notify("Hello!", "info", { title = "Neovim" })
      end, 1000)
    end,
  },
}

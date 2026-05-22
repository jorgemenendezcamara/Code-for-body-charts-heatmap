library(ggplot2)
library(readr)
library(tidyr)
library(dplyr)
library(png)
library(grid)
library(optparse)

# === Parse command line arguments ===
option_list <- list(
  make_option(c("--matrix_path"), type="character", default=NULL,
              help="Path to heatmap matrix CSV file (required)"),
  make_option(c("--template_path"), type="character", default=NULL,
              help="Path to template PNG image (required)"),
  make_option(c("--output_plot"), type="character", default="heatmap_overlay.png",
              help="Output filename for the plot (default: heatmap_overlay.png)"),
  make_option(c("--alpha"), type="double", default=0.6,
              help="Transparency of heatmap overlay (default: 0.6)"),
  make_option(c("--plot_width"), type="integer", default=8,
              help="Plot width in inches (default: 8)"),
  make_option(c("--plot_height"), type="integer", default=12,
              help="Plot height in inches (default: 12)")
)

opt_parser <- OptionParser(option_list=option_list)
opt <- parse_args(opt_parser)

# Validate required arguments
if (is.null(opt$matrix_path) || is.null(opt$template_path)) {
  print_help(opt_parser)
  stop("Both --matrix_path and --template_path are required", call.=FALSE)
}

# === 1. Read CSV exported from Python ===
heatmap <- read_csv(opt$matrix_path, col_names = FALSE)

# === 2. Convert from wide to long format and set NA for zero values ===
heatmap_long <- heatmap %>%
  mutate(y = row_number()) %>%
  pivot_longer(-y, names_to = "x", values_to = "value") %>%
  mutate(x = as.integer(factor(x, levels = unique(x))),
         value_plot = ifelse(value == 0, NA, value))

# === 3. Get matrix dimensions ===
nx <- max(heatmap_long$x)
ny <- max(heatmap_long$y)

# === 4. Load template image ===
template <- readPNG(opt$template_path)
template_grob <- rasterGrob(template,
                            width = unit(1, "npc"),
                            height = unit(1, "npc"),
                            interpolate = TRUE)

# === 5. Create heatmap overlay plot ===
heatmap_plot <- ggplot(heatmap_long, aes(x = x, y = ny - y, fill = value)) +
  annotation_custom(template_grob, xmin=0, xmax=nx, ymin=0, ymax=ny) +
  geom_raster(aes(fill = value_plot), alpha = opt$alpha, interpolate = TRUE) +
  scale_fill_gradientn(
    colours = c("white", "yellow", "orange", "red"),
    limits = c(0, 1),
    na.value = "white",
    name = "Percentage of patients",
    labels = function(x) round(x * 100)
  ) +
  coord_fixed() +
  theme_void() +
  theme(
    legend.position = "right",
    legend.title = element_text(size = 10),
    legend.text = element_text(size = 8)
  )

# === 6. Save plot ===
ggsave(opt$output_plot, plot = heatmap_plot, 
       width = opt$plot_width, height = opt$plot_height, dpi = 300)

cat("eatmap plot saved to:", opt$output_plot, "\n")

# === 7. Optionally display plot ===
if (interactive()) {
  print(heatmap_plot)
}
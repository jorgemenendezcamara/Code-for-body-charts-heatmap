import cv2
import numpy as np
import matplotlib.pyplot as plt
import glob
import pandas as pd
import os
import argparse

def generate_heatmap_matrix(input_dir, template_pattern="*.png", exclude_template=True):
    """
    Generate heatmap matrix from patient body chart PNGs.
    
    Parameters:
    -----------
    input_dir : str
        Directory containing patient PNG files
    template_pattern : str
        Pattern to identify template file (e.g., "template.png" or "Right Hand.png")
    exclude_template : bool
        Whether to exclude files matching template_pattern from analysis
    
    Returns:
    --------
    heatmap_norm : numpy.ndarray
        Normalized heatmap matrix (0-1 range)
    n_patients : int
        Number of patients processed
    """
    
    # Get all PNG files
    archivos = glob.glob(os.path.join(input_dir, "*.png"))
    
    if exclude_template:
        # Filter out template file (files that don't start with digit, or use pattern)
        # Adjust this condition based on your naming convention
        archivos = [f for f in archivos if not template_pattern in os.path.basename(f)]
    
    n_pacientes = len(archivos)
    print(f"Processing {n_pacientes} patients...")
    
    if n_pacientes == 0:
        raise FileNotFoundError(f"No PNG files found in {input_dir}")
    
    heatmap = None
    
    for archivo in archivos:
        img = cv2.imread(archivo, cv2.IMREAD_UNCHANGED)
        if img is None:
            print(f"⚠️ Could not read {archivo}, skipping.")
            continue
        
        # Detect painted areas (RGBA vs RGB)
        if img.shape[2] == 4:  
            # Use alpha channel if available
            mask = (img[:, :, 3] > 0).astype(np.uint8)
        else:
            # Convert to grayscale and threshold for RGB
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            mask = (gray < 200).astype(np.uint8)
        
        # Accumulate heatmap
        if heatmap is None:
            heatmap = mask
        else:
            heatmap += mask
    
    # Normalize by number of patients
    heatmap = heatmap.astype(np.float32)
    heatmap_norm = heatmap / n_pacientes
    
    return heatmap_norm, n_pacientes


def save_heatmap_visualization(heatmap_norm, output_path, title="Heatmap of Patient Selections"):
    """
    Save a visualization of the heatmap (ROIs only).
    
    Parameters:
    -----------
    heatmap_norm : numpy.ndarray
        Normalized heatmap matrix (0-1 range)
    output_path : str
        Path where to save the visualization
    title : str
        Title for the plot
    """
    # Invert for visualization (hot areas become brighter)
    heatmap_norm_inv = 1 - heatmap_norm
    
    # Apply colormap
    colored_heatmap = cv2.applyColorMap(
        np.uint8(255 * heatmap_norm_inv), cv2.COLORMAP_HOT
    )
    colored_heatmap = cv2.cvtColor(colored_heatmap, cv2.COLOR_BGR2RGB)
    
    # Plot
    plt.figure(figsize=(8, 12))
    plt.imshow(colored_heatmap)
    plt.title(title)
    plt.axis("off")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    
    print(f"✅ Heatmap visualization saved to: {output_path}")


def save_matrix_csv(heatmap_norm, output_path):
    """
    Save heatmap matrix as CSV for R processing.
    
    Parameters:
    -----------
    heatmap_norm : numpy.ndarray
        Normalized heatmap matrix (0-1 range)
    output_path : str
        Path where to save the CSV
    """
    pd.DataFrame(heatmap_norm).to_csv(output_path, index=False, header=False)
    print(f"✅ Matrix CSV saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Generate heatmap matrix from body chart PNGs')
    parser.add_argument('--input_dir', type=str, required=True,
                        help='Directory containing patient PNG files')
    parser.add_argument('--output_dir', type=str, default=None,
                        help='Output directory (default: same as input_dir)')
    parser.add_argument('--template_pattern', type=str, default="template",
                        help='Pattern to identify template file (default: "template")')
    parser.add_argument('--visualization_name', type=str, default="heatmap_rois_only.png",
                        help='Output filename for visualization')
    parser.add_argument('--matrix_name', type=str, default="heatmap_matrix.csv",
                        help='Output filename for CSV matrix')
    
    args = parser.parse_args()
    
    # Set output directory
    output_dir = args.output_dir if args.output_dir else args.input_dir
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate heatmap matrix
    heatmap_norm, n_patients = generate_heatmap_matrix(
        args.input_dir, 
        template_pattern=args.template_pattern
    )
    
    print(f"✅ Processed {n_patients} patients")
    print(f"📊 Heatmap dimensions: {heatmap_norm.shape}")
    
    # Save outputs
    vis_path = os.path.join(output_dir, args.visualization_name)
    save_heatmap_visualization(heatmap_norm, vis_path)
    
    matrix_path = os.path.join(output_dir, args.matrix_name)
    save_matrix_csv(heatmap_norm, matrix_path)


if __name__ == "__main__":
    main()
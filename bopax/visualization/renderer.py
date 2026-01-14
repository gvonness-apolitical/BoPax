"""3D Visualization of packing solutions."""
import json
import random
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.patches import Patch
import numpy as np


def generate_color():
    """Generate a random pastel color."""
    r = random.uniform(0.5, 1.0)
    g = random.uniform(0.5, 1.0)
    b = random.uniform(0.5, 1.0)
    return (r, g, b, 0.7)


def create_box_vertices(position, dimensions):
    """Create vertices for a 3D box."""
    x, y, z = position
    w, d, h = dimensions

    vertices = [
        [x, y, z],
        [x + w, y, z],
        [x + w, y + d, z],
        [x, y + d, z],
        [x, y, z + h],
        [x + w, y, z + h],
        [x + w, y + d, z + h],
        [x, y + d, z + h]
    ]

    return np.array(vertices)


def create_box_faces(vertices):
    """Create faces for a 3D box from vertices."""
    faces = [
        [vertices[0], vertices[1], vertices[5], vertices[4]],
        [vertices[2], vertices[3], vertices[7], vertices[6]],
        [vertices[0], vertices[3], vertices[7], vertices[4]],
        [vertices[1], vertices[2], vertices[6], vertices[5]],
        [vertices[0], vertices[1], vertices[2], vertices[3]],
        [vertices[4], vertices[5], vertices[6], vertices[7]]
    ]

    return faces


def plot_container(container_data: Dict, container_id: int,
                   azimuth: int = 45,
                   box_type_colors: Optional[Dict] = None):
    """Create a 3D plot for a single container.

    Args:
        container_data: Container information dict from packing result
        container_id: ID number for the container
        azimuth: Viewing angle for the 3D plot
        box_type_colors: Optional dict of colors for each box type

    Returns:
        Tuple of (figure, box_type_colors dict)
    """
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')

    container_dims = container_data['dimensions']
    container_label = container_data['type']

    # Draw container outline
    vertices = create_box_vertices((0, 0, 0), container_dims)
    faces = create_box_faces(vertices)

    container_outline = Poly3DCollection(faces, alpha=0.1, facecolor='gray',
                                        edgecolor='black', linewidth=2)
    ax.add_collection3d(container_outline)

    if box_type_colors is None:
        box_type_colors = {}

    # Draw each packed box
    for box in container_data['boxes']:
        position = tuple(box['position'])
        dimensions = tuple(box['placed_dimensions'])
        box_label = box['label']

        if box_label not in box_type_colors:
            box_type_colors[box_label] = generate_color()

        color = box_type_colors[box_label]

        vertices = create_box_vertices(position, dimensions)
        faces = create_box_faces(vertices)

        box_poly = Poly3DCollection(faces, alpha=0.7, facecolor=color,
                                    edgecolor='black', linewidth=0.5)
        ax.add_collection3d(box_poly)

        # Add label at box center
        center_x = position[0] + dimensions[0] / 2
        center_y = position[1] + dimensions[1] / 2
        center_z = position[2] + dimensions[2] / 2

        short_label = f"#{box['box_id']}"
        ax.text(center_x, center_y, center_z, short_label,
               fontsize=7, ha='center', va='center')

    ax.set_xlabel('Width (mm)', fontsize=10)
    ax.set_ylabel('Depth (mm)', fontsize=10)
    ax.set_zlabel('Height (mm)', fontsize=10)

    title = f"Container #{container_id}: {container_label}\n"
    title += f"Dimensions: {container_dims[0]}x{container_dims[1]}x{container_dims[2]} mm\n"
    title += f"Utilization: {container_data['utilization']:.1%} "
    title += f"({len(container_data['boxes'])} boxes)"
    ax.set_title(title, fontsize=12, fontweight='bold')

    ax.set_xlim(0, container_dims[0])
    ax.set_ylim(0, container_dims[1])
    ax.set_zlim(0, container_dims[2])

    max_dim = max(container_dims)
    ax.set_box_aspect((container_dims[0]/max_dim,
                       container_dims[1]/max_dim,
                       container_dims[2]/max_dim))

    # Add legend
    legend_elements = []
    for box_label, color in sorted(box_type_colors.items()):
        count = sum(1 for b in container_data['boxes'] if b['label'] == box_label)
        legend_elements.append(Patch(facecolor=color, edgecolor='black',
                                     label=f"{box_label} ({count})"))

    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.05, 1),
             fontsize=8)

    ax.view_init(elev=20, azim=azimuth)

    plt.tight_layout()

    return fig, box_type_colors


def create_summary_plot(result: Dict):
    """Create a summary plot showing all containers.

    Args:
        result: Packing result dictionary

    Returns:
        Matplotlib figure
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Packing Solution Summary', fontsize=16, fontweight='bold')

    # Plot 1: Container utilization
    ax1 = axes[0, 0]
    container_ids = [f"C{c['id']}" for c in result['containers']]
    utilizations = [c['utilization'] * 100 for c in result['containers']]
    colors_util = ['green' if u > 75 else 'orange' if u > 50 else 'red'
                   for u in utilizations]

    ax1.bar(container_ids, utilizations, color=colors_util, alpha=0.7, edgecolor='black')
    ax1.axhline(y=75, color='green', linestyle='--', alpha=0.5, label='75% target')
    ax1.set_ylabel('Utilization (%)', fontsize=11)
    ax1.set_xlabel('Container', fontsize=11)
    ax1.set_title('Container Utilization', fontsize=12, fontweight='bold')
    ax1.set_ylim(0, 100)
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)

    # Plot 2: Container type distribution
    ax2 = axes[0, 1]
    container_types = list(result['container_counts'].keys())
    counts = list(result['container_counts'].values())
    colors_types = plt.cm.Set3(range(len(container_types)))

    ax2.pie(counts, labels=container_types, autopct='%1.0f%%',
           colors=colors_types, startangle=90, textprops={'fontsize': 10})
    ax2.set_title('Container Type Distribution', fontsize=12, fontweight='bold')

    # Plot 3: Volume breakdown
    ax3 = axes[1, 0]
    used_volume = result['total_volume_used']
    wasted_volume = result['total_volume_available'] - used_volume

    volumes = [used_volume / 1e6, wasted_volume / 1e6]
    labels = [f"Used\n({used_volume:,} mm3)", f"Wasted\n({wasted_volume:,} mm3)"]
    colors_vol = ['#4CAF50', '#FFC107']

    ax3.bar(labels, volumes, color=colors_vol, alpha=0.7, edgecolor='black')
    ax3.set_ylabel('Volume (Liters)', fontsize=11)
    ax3.set_title('Volume Usage', fontsize=12, fontweight='bold')
    ax3.grid(axis='y', alpha=0.3)

    # Plot 4: Summary statistics
    ax4 = axes[1, 1]
    ax4.axis('off')

    stats_text = f"""
    SUMMARY STATISTICS
    {'='*40}

    Total Containers:      {result['total_containers']}

    Container Types:
    """

    for ctype, count in sorted(result['container_counts'].items()):
        stats_text += f"      - {ctype}: {count}\n"

    stats_text += f"""
    Total Volume Used:     {result['total_volume_used']:,} mm3
    Total Volume Available: {result['total_volume_available']:,} mm3
    Overall Utilization:   {result['overall_utilization']:.1%}

    Efficiency Rating:     """

    rating = result['overall_utilization']
    if rating > 0.8:
        stats_text += "Excellent"
    elif rating > 0.65:
        stats_text += "Good"
    elif rating > 0.5:
        stats_text += "Fair"
    else:
        stats_text += "Poor"

    ax4.text(0.1, 0.5, stats_text, fontsize=11, verticalalignment='center',
            fontfamily='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

    plt.tight_layout()

    return fig


def visualize_packing(json_file: str = 'packing_result.json',
                      save_images: bool = True,
                      output_dir: str = '.'):
    """Main visualization function.

    Args:
        json_file: Path to the packing result JSON file
        save_images: Whether to save images to files
        output_dir: Directory to save output images

    Returns:
        List of generated figure objects
    """
    import os

    print(f"Loading packing results from {json_file}...")

    with open(json_file, 'r') as f:
        result = json.load(f)

    print(f"Found {result['total_containers']} containers to visualize")

    figures = []

    # Create summary plot
    print("\nCreating summary plot...")
    summary_fig = create_summary_plot(result)
    figures.append(summary_fig)

    if save_images:
        summary_path = os.path.join(output_dir, 'packing_summary.png')
        summary_fig.savefig(summary_path, dpi=150, bbox_inches='tight')
        print(f"Saved {summary_path}")

    # Create individual container plots
    for container in result['containers']:
        container_id = container['id']
        print(f"\nCreating 3D visualizations for Container #{container_id}...")

        fig1, box_colors = plot_container(container, container_id, azimuth=45)
        figures.append(fig1)

        if save_images:
            filename1 = os.path.join(output_dir, f"container_{container_id:02d}_view1.png")
            fig1.savefig(filename1, dpi=150, bbox_inches='tight')
            print(f"Saved {filename1}")

        plt.close(fig1)

        fig2, _ = plot_container(container, container_id, azimuth=225,
                                 box_type_colors=box_colors)
        figures.append(fig2)

        if save_images:
            filename2 = os.path.join(output_dir, f"container_{container_id:02d}_view2.png")
            fig2.savefig(filename2, dpi=150, bbox_inches='tight')
            print(f"Saved {filename2}")

        plt.close(fig2)

    print("\n" + "="*60)
    print("Visualization complete!")
    print("="*60)

    return figures

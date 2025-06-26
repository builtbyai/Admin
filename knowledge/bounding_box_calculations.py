# Bounding Box Calculation Examples

def calculate_bounding_box(text_position):
    """Calculate bounding box from text position and size"""
    x1 = text_position['x']
    y1 = text_position['y']
    x2 = x1 + text_position['width']
    y2 = y1 + text_position['height']
    return [x1, y1, x2, y2]

def calculate_center_point(bbox):
    """Find center point of bounding box"""
    return {
        'x': (bbox[0] + bbox[2]) / 2,
        'y': (bbox[1] + bbox[3]) / 2
    }

def calculate_distances(elem1_bbox, elem2_bbox):
    """Calculate distances between elements"""
    # Horizontal distance (edge to edge)
    if elem1_bbox[2] <= elem2_bbox[0]:  # elem1 is left of elem2
        horizontal = elem2_bbox[0] - elem1_bbox[2]
    elif elem2_bbox[2] <= elem1_bbox[0]:  # elem2 is left of elem1
        horizontal = elem1_bbox[0] - elem2_bbox[2]
    else:  # overlapping horizontally
        horizontal = 0
    
    # Vertical distance (edge to edge)
    if elem1_bbox[3] <= elem2_bbox[1]:  # elem1 is above elem2
        vertical = elem2_bbox[1] - elem1_bbox[3]
    elif elem2_bbox[3] <= elem1_bbox[1]:  # elem2 is above elem1
        vertical = elem1_bbox[1] - elem2_bbox[3]
    else:  # overlapping vertically
        vertical = 0
    
    return {
        'horizontal': horizontal,
        'vertical': vertical,
        'euclidean': (horizontal**2 + vertical**2)**0.5
    }

def check_alignment(bbox1, bbox2, tolerance=5):
    """Check if two elements are aligned"""
    return {
        'left_aligned': abs(bbox1[0] - bbox2[0]) <= tolerance,
        'right_aligned': abs(bbox1[2] - bbox2[2]) <= tolerance,
        'top_aligned': abs(bbox1[1] - bbox2[1]) <= tolerance,
        'bottom_aligned': abs(bbox1[3] - bbox2[3]) <= tolerance,
        'center_x_aligned': abs((bbox1[0] + bbox1[2])/2 - (bbox2[0] + bbox2[2])/2) <= tolerance,
        'center_y_aligned': abs((bbox1[1] + bbox1[3])/2 - (bbox2[1] + bbox2[3])/2) <= tolerance
    }

def calculate_overlap(bbox1, bbox2):
    """Calculate overlap area between two bounding boxes"""
    x_overlap = max(0, min(bbox1[2], bbox2[2]) - max(bbox1[0], bbox2[0]))
    y_overlap = max(0, min(bbox1[3], bbox2[3]) - max(bbox1[1], bbox2[1]))
    overlap_area = x_overlap * y_overlap
    
    area1 = (bbox1[2] - bbox1[0]) * (bbox1[3] - bbox1[1])
    area2 = (bbox2[2] - bbox2[0]) * (bbox2[3] - bbox2[1])
    
    return {
        'overlap_area': overlap_area,
        'overlap_percentage_1': (overlap_area / area1) * 100 if area1 > 0 else 0,
        'overlap_percentage_2': (overlap_area / area2) * 100 if area2 > 0 else 0
    }

def detect_grid_layout(bboxes, tolerance=10):
    """Detect if elements follow a grid layout"""
    if len(bboxes) < 4:
        return False
    
    # Extract unique x and y coordinates
    x_coords = set()
    y_coords = set()
    
    for bbox in bboxes:
        x_coords.add(bbox[0])  # left edge
        x_coords.add(bbox[2])  # right edge
        y_coords.add(bbox[1])  # top edge
        y_coords.add(bbox[3])  # bottom edge
    
    # Check if coordinates form regular intervals
    x_sorted = sorted(x_coords)
    y_sorted = sorted(y_coords)
    
    # Calculate intervals
    x_intervals = [x_sorted[i+1] - x_sorted[i] for i in range(len(x_sorted)-1)]
    y_intervals = [y_sorted[i+1] - y_sorted[i] for i in range(len(y_sorted)-1)]
    
    # Check if intervals are consistent (within tolerance)
    x_consistent = len(set(round(interval/tolerance)*tolerance for interval in x_intervals)) <= 2
    y_consistent = len(set(round(interval/tolerance)*tolerance for interval in y_intervals)) <= 2
    
    return x_consistent and y_consistent

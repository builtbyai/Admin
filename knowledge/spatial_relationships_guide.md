# Spatial Relationships Guide

## Position Descriptors

### Absolute Positions
- **top-left**: Upper left corner region (0-33% x, 0-33% y)
- **top-center**: Upper center region (33-66% x, 0-33% y)
- **top-right**: Upper right corner region (66-100% x, 0-33% y)
- **middle-left**: Left center region (0-33% x, 33-66% y)
- **center**: Central region (33-66% x, 33-66% y)
- **middle-right**: Right center region (66-100% x, 33-66% y)
- **bottom-left**: Lower left corner region (0-33% x, 66-100% y)
- **bottom-center**: Lower center region (33-66% x, 66-100% y)
- **bottom-right**: Lower right corner region (66-100% x, 66-100% y)

### Relative Positions
- **above**: Element A's bottom edge is above element B's top edge
- **below**: Element A's top edge is below element B's bottom edge
- **left-of**: Element A's right edge is left of element B's left edge
- **right-of**: Element A's left edge is right of element B's right edge
- **overlapping**: Elements share any common area
- **contained-within**: Element A is completely inside element B
- **adjacent**: Elements are touching or very close (< 10px apart)

## Alignment Types

### Horizontal Alignment
- **left-aligned**: x1 coordinates match within tolerance
- **right-aligned**: x2 coordinates match within tolerance
- **center-aligned**: center x coordinates match within tolerance
- **justified**: Both left and right edges align with container

### Vertical Alignment
- **top-aligned**: y1 coordinates match within tolerance
- **bottom-aligned**: y2 coordinates match within tolerance
- **middle-aligned**: center y coordinates match within tolerance
- **baseline-aligned**: Text baselines match (for text elements)

### Grid Alignment
- **column-aligned**: Elements share common x-coordinates
- **row-aligned**: Elements share common y-coordinates
- **grid-positioned**: Elements follow regular spacing pattern

## Distance Calculations

### Edge-to-Edge Distance
```python
def edge_distance(bbox1, bbox2):
    # Horizontal distance
    if bbox1[2] <= bbox2[0]:  # bbox1 left of bbox2
        h_dist = bbox2[0] - bbox1[2]
    elif bbox2[2] <= bbox1[0]:  # bbox2 left of bbox1
        h_dist = bbox1[0] - bbox2[2]
    else:  # overlapping
        h_dist = 0
    
    # Vertical distance
    if bbox1[3] <= bbox2[1]:  # bbox1 above bbox2
        v_dist = bbox2[1] - bbox1[3]
    elif bbox2[3] <= bbox1[1]:  # bbox2 above bbox1
        v_dist = bbox1[1] - bbox2[3]
    else:  # overlapping
        v_dist = 0
    
    return h_dist, v_dist
```

### Center-to-Center Distance
```python
def center_distance(bbox1, bbox2):
    center1 = ((bbox1[0] + bbox1[2]) / 2, (bbox1[1] + bbox1[3]) / 2)
    center2 = ((bbox2[0] + bbox2[2]) / 2, (bbox2[1] + bbox2[3]) / 2)
    
    dx = center2[0] - center1[0]
    dy = center2[1] - center1[1]
    
    return (dx**2 + dy**2)**0.5
```

### Relative Position Percentage
```python
def relative_position(bbox, container):
    rel_x = (bbox[0] - container[0]) / (container[2] - container[0])
    rel_y = (bbox[1] - container[1]) / (container[3] - container[1])
    
    return rel_x * 100, rel_y * 100
```

## Text Flow Indicators

### Reading Order
- **sequential**: Elements follow natural reading order (left-to-right, top-to-bottom)
- **columnar**: Text flows in columns before moving to next row
- **reverse**: Right-to-left or bottom-to-top reading order
- **non-linear**: No clear sequential pattern

### Hierarchy Levels
- **h1-h6**: Standard heading hierarchy
- **title**: Document or section title
- **subtitle**: Secondary title
- **body**: Regular paragraph text
- **caption**: Image or table caption
- **footnote**: Reference or additional information

### Text Relationships
- **continues-from**: Text element continues from previous element
- **continues-to**: Text element continues to next element
- **references**: Element references another element
- **labels**: Element serves as label for another element

## Proximity Rules

### Grouping by Distance
- **Very Close**: < 5px apart (likely same element)
- **Close**: 5-15px apart (related elements)
- **Near**: 15-30px apart (possibly related)
- **Distant**: 30-50px apart (separate groups)
- **Far**: > 50px apart (unrelated)

### Visual Grouping
- **whitespace-separated**: Groups separated by significant whitespace
- **border-separated**: Groups separated by lines or borders
- **color-grouped**: Elements with similar colors
- **size-grouped**: Elements with similar dimensions
- **alignment-grouped**: Elements sharing alignment

## Layout Patterns

### Common Structures
- **header-content-footer**: Three-section vertical layout
- **sidebar-main**: Two-column horizontal layout
- **grid**: Regular matrix of elements
- **list**: Vertical sequence of similar elements
- **card**: Grouped content with clear boundaries

### Responsive Patterns
- **stack-on-mobile**: Horizontal elements become vertical
- **hide-on-small**: Elements hidden at smaller sizes
- **reorder**: Element order changes based on screen size
- **scale**: Elements resize proportionally

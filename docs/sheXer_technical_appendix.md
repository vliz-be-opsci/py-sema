# sheXer Integration Technical Appendix

## Detailed Compatibility Analysis

### Dependency Comparison

| Library | py-sema Current | sheXer 2.7.0 | Compatibility |
|---------|----------------|---------------|---------------|
| rdflib | ^7.0.0 | >= 5.0.0 | ✅ Compatible |
| Flask | Not used | Required | ⚠️ New dependency |
| SPARQLWrapper | Not explicitly listed | Required | ⚠️ New dependency |
| plantuml | Not used | Required | ⚠️ Optional feature |

### Integration Architecture

```python
# sema/shapes/__init__.py
from typing import Optional, List, Union
import logging

log = logging.getLogger(__name__)

# Graceful import with fallback
try:
    from shexer import Shaper
    SHEXER_AVAILABLE = True
except ImportError:
    log.warning("sheXer not available. Install with: pip install shexer")
    SHEXER_AVAILABLE = False
    Shaper = None

__all__ = ["ShapeGenerator", "SHEXER_AVAILABLE"]

class ShapeGenerator:
    """Wrapper for sheXer functionality with graceful degradation"""
    
    def __init__(self, **kwargs):
        if not SHEXER_AVAILABLE:
            raise ImportError("sheXer library not available. Install with: pip install 'pysema[shapes]'")
        
        self._shaper = Shaper(**kwargs)
    
    def generate_from_graph(self, graph_path: str, format: str = "shex") -> str:
        """Generate shapes from RDF graph file"""
        if format.lower() == "shacl":
            return self._shaper.shacl_graph(rdf_graph_file_path=graph_path)
        else:
            return self._shaper.shex_graph(rdf_graph_file_path=graph_path)
```

## Specific API Integration Examples

### Example 1: Benchmarking Enhancement

```python
# sema/bench/handlers/shape_generation.py
from typing import Optional, Dict, Any
from pathlib import Path
from ..handler import TaskHandler
from ...shapes import ShapeGenerator, SHEXER_AVAILABLE

class ShapeGenerationHandler(TaskHandler):
    """Generate shapes from RDF data for benchmarking"""
    
    def handle(self, task) -> Dict[str, Any]:
        if not SHEXER_AVAILABLE:
            self.logger.warning("sheXer not available, skipping shape generation")
            return {"status": "skipped", "reason": "sheXer not installed"}
        
        try:
            # Configure shape generation based on task args
            generator_config = {
                "target_classes": task.args.get("target_classes"),
                "output_format": task.args.get("output_format", "shacl"),
                "tolerance": task.args.get("tolerance", 1.0),
                "disable_comments": task.args.get("disable_comments", True)
            }
            
            # Remove None values
            generator_config = {k: v for k, v in generator_config.items() if v is not None}
            
            generator = ShapeGenerator(**generator_config)
            
            # Generate shapes
            input_path = Path(task.input_data_location) / task.args["data_graph"]
            shapes_content = generator.generate_from_graph(
                str(input_path), 
                format=task.args.get("output_format", "shacl")
            )
            
            # Save shapes
            output_path = Path(task.output_location) / f"generated_shapes.{task.args.get('output_format', 'shacl')}"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(shapes_content)
            
            return {
                "status": "success",
                "shapes_file": str(output_path),
                "classes_analyzed": len(generator_config.get("target_classes", [])),
                "output_format": task.args.get("output_format", "shacl")
            }
            
        except Exception as e:
            self.logger.error(f"Shape generation failed: {e}")
            return {"status": "error", "error": str(e)}

# Update dispatcher to include new handler
# sema/bench/dispatcher.py
class TaskDispatcher:
    def dispatch(self, task):
        handlers = {
            "shacl": ShaclHandler,
            "shape_generation": ShapeGenerationHandler,  # NEW
            "subyt": SubytHandler,
            # ... existing handlers
        }
        return handlers.get(task.task_type, TaskHandler)
```

### Example 2: Harvest Integration

```python
# sema/harvest/shape_analyzer.py
from typing import Dict, List, Optional
from rdflib import Graph, URIRef
from pathlib import Path
import tempfile

from ..shapes import ShapeGenerator, SHEXER_AVAILABLE
from ..commons.log import get_logger

log = get_logger(__name__)

class HarvestShapeAnalyzer:
    """Analyze shapes from harvested RDF data"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get("enable_shape_analysis", False) and SHEXER_AVAILABLE
        
        if self.enabled:
            self.generator = ShapeGenerator(
                tolerance=config.get("shape_tolerance", 0.9),
                output_format=ShapeGenerator.SHACL_TURTLE,
                disable_comments=True
            )
    
    def analyze_harvested_data(self, graph: Graph) -> Optional[Dict[str, Any]]:
        """Analyze structural patterns in harvested RDF data"""
        if not self.enabled:
            log.debug("Shape analysis disabled or sheXer not available")
            return None
        
        try:
            # Extract classes from the graph
            classes = self._extract_classes(graph)
            if not classes:
                log.info("No classes found in harvested data")
                return None
            
            # Create temporary file for shape generation
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ttl', delete=False) as tmp_file:
                graph.serialize(destination=tmp_file.name, format='turtle')
                temp_path = tmp_file.name
            
            try:
                # Generate shapes
                self.generator._shaper.target_classes = [str(cls) for cls in classes]
                shapes_content = self.generator.generate_from_graph(temp_path, format="shacl")
                
                # Parse generated shapes to extract insights
                shapes_graph = Graph()
                shapes_graph.parse(data=shapes_content, format='turtle')
                
                analysis = {
                    "classes_analyzed": len(classes),
                    "shapes_generated": len(list(shapes_graph.subjects())),
                    "classes": [str(cls) for cls in classes],
                    "shapes_content": shapes_content,
                    "insights": self._extract_shape_insights(shapes_graph)
                }
                
                return analysis
                
            finally:
                # Clean up temporary file
                Path(temp_path).unlink(missing_ok=True)
                
        except Exception as e:
            log.error(f"Shape analysis failed: {e}")
            return {"error": str(e)}
    
    def _extract_classes(self, graph: Graph) -> List[URIRef]:
        """Extract unique classes from RDF graph"""
        from rdflib import RDF
        
        classes = set()
        for _, _, obj in graph.triples((None, RDF.type, None)):
            if isinstance(obj, URIRef):
                classes.add(obj)
        
        return list(classes)
    
    def _extract_shape_insights(self, shapes_graph: Graph) -> Dict[str, Any]:
        """Extract insights from generated shapes"""
        from rdflib.namespace import SH
        
        insights = {
            "property_constraints": 0,
            "cardinality_constraints": 0,
            "datatype_constraints": 0
        }
        
        # Count different types of constraints
        for _, _, _ in shapes_graph.triples((None, SH.property, None)):
            insights["property_constraints"] += 1
        
        for _, _, _ in shapes_graph.triples((None, SH.minCount, None)):
            insights["cardinality_constraints"] += 1
            
        for _, _, _ in shapes_graph.triples((None, SH.datatype, None)):
            insights["datatype_constraints"] += 1
        
        return insights

# Integration with existing harvest service
# sema/harvest/service.py (additions)
class Harvest(ServiceBase):
    def __init__(self, config: str, target_store_info: Optional[List[str]] = None):
        super().__init__()
        # ... existing initialization ...
        
        # NEW: Initialize shape analyzer
        self.shape_analyzer = HarvestShapeAnalyzer(self.config.get("shape_analysis", {}))
    
    def process(self) -> HarvestResult:
        result = super().process()
        
        # NEW: Analyze shapes if enabled
        if self.shape_analyzer.enabled and result.success:
            log.info("Analyzing structural patterns in harvested data")
            shape_analysis = self.shape_analyzer.analyze_harvested_data(result.graph)
            
            if shape_analysis:
                result.shape_analysis = shape_analysis
                log.info(f"Shape analysis completed: {shape_analysis['classes_analyzed']} classes analyzed")
                
                # Optionally save shapes to file
                if self.config.get("save_generated_shapes", False):
                    shapes_file = self.config.output_dir / "generated_shapes.ttl"
                    with open(shapes_file, 'w', encoding='utf-8') as f:
                        f.write(shape_analysis['shapes_content'])
                    log.info(f"Generated shapes saved to {shapes_file}")
        
        return result
```

## CLI Integration Implementation

```python
# sema/shapes/__main__.py
"""Command-line interface for shape generation"""
import argparse
import sys
from pathlib import Path
from typing import List, Optional

from ..commons.cli import SemaArgsParser
from .generator import ShapeGenerator, SHEXER_AVAILABLE

def create_arg_parser() -> SemaArgsParser:
    parser = SemaArgsParser(
        prog="sema-shapes",
        description="Generate shapes from RDF data using sheXer"
    )
    
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Input RDF file path"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: stdout)"
    )
    
    parser.add_argument(
        "--format", "-f",
        choices=["shex", "shacl"],
        default="shacl",
        help="Output format (default: shacl)"
    )
    
    parser.add_argument(
        "--classes", "-c",
        help="Comma-separated list of target classes (default: all classes)"
    )
    
    parser.add_argument(
        "--tolerance", "-t",
        type=float,
        default=1.0,
        help="Tolerance for shape generation (0.0-1.0, default: 1.0)"
    )
    
    parser.add_argument(
        "--namespaces", "-n",
        help="Path to namespaces configuration file"
    )
    
    return parser

def main():
    if not SHEXER_AVAILABLE:
        print("Error: sheXer library not available.", file=sys.stderr)
        print("Install with: pip install 'pysema[shapes]'", file=sys.stderr)
        sys.exit(1)
    
    parser = create_arg_parser()
    args = parser.parse_args()
    
    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Parse target classes
        target_classes = None
        if args.classes:
            target_classes = [cls.strip() for cls in args.classes.split(",")]
        
        # Configure shape generator
        generator_config = {
            "target_classes": target_classes,
            "tolerance": args.tolerance,
            "disable_comments": True
        }
        
        # Load namespaces if provided
        if args.namespaces:
            # TODO: Implement namespace loading
            pass
        
        generator = ShapeGenerator(**generator_config)
        
        # Generate shapes
        shapes_content = generator.generate_from_graph(str(input_path), format=args.format)
        
        # Output shapes
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(shapes_content)
            print(f"Shapes written to {output_path}")
        else:
            print(shapes_content)
            
    except Exception as e:
        print(f"Error generating shapes: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## Configuration Examples

### Harvest with Shape Analysis
```yaml
# harvest_config.yml
harvest:
  sources:
    - uri: "https://example.org/data.ttl"
      format: "turtle"

shape_analysis:
  enable_shape_analysis: true
  shape_tolerance: 0.8
  save_generated_shapes: true
  output_format: "shacl"
```

### Benchmarking with Shape Generation
```yaml
# sembench_config.yml
tasks:
  - name: "generate_test_shapes"
    type: "shape_generation"
    args:
      data_graph: "sample_data.ttl"
      output_format: "shacl"
      target_classes: ["foaf:Person", "schema:Organization"]
      tolerance: 0.9
  
  - name: "validate_with_generated_shapes"
    type: "shacl"
    depends_on: ["generate_test_shapes"]
    args:
      data_graph: "test_data.ttl"
      shacl_graph: "generated_shapes.shacl"
```

## Performance Considerations

### Memory Management
```python
# sema/shapes/performance.py
import psutil
import logging
from typing import Optional

log = logging.getLogger(__name__)

class MemoryMonitor:
    """Monitor memory usage during shape generation"""
    
    def __init__(self, max_memory_mb: Optional[int] = None):
        self.max_memory_mb = max_memory_mb or 1024  # Default 1GB limit
        self.start_memory = None
    
    def __enter__(self):
        self.start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_memory:
            current_memory = psutil.Process().memory_info().rss / 1024 / 1024
            memory_used = current_memory - self.start_memory
            log.info(f"Shape generation used {memory_used:.2f} MB of memory")
            
            if memory_used > self.max_memory_mb:
                log.warning(f"Memory usage ({memory_used:.2f} MB) exceeded limit ({self.max_memory_mb} MB)")

# Usage in shape generator
class OptimizedShapeGenerator(ShapeGenerator):
    def generate_from_graph(self, graph_path: str, format: str = "shex", 
                          memory_limit_mb: Optional[int] = None) -> str:
        with MemoryMonitor(memory_limit_mb):
            return super().generate_from_graph(graph_path, format)
```

## Testing Strategy

```python
# tests/shapes/test_integration.py
import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from sema.shapes import ShapeGenerator, SHEXER_AVAILABLE

@pytest.mark.skipif(not SHEXER_AVAILABLE, reason="sheXer not available")
class TestShapeGenerator:
    
    def test_basic_shape_generation(self, sample_rdf_file):
        generator = ShapeGenerator()
        shapes = generator.generate_from_graph(str(sample_rdf_file), format="shacl")
        
        assert shapes is not None
        assert "sh:NodeShape" in shapes or "sh:PropertyShape" in shapes
    
    def test_graceful_degradation_without_shexer(self):
        with patch('sema.shapes.SHEXER_AVAILABLE', False):
            with pytest.raises(ImportError, match="sheXer library not available"):
                ShapeGenerator()

@pytest.fixture
def sample_rdf_file(tmp_path):
    """Create a sample RDF file for testing"""
    rdf_content = """
    @prefix ex: <http://example.org/> .
    @prefix foaf: <http://xmlns.com/foaf/0.1/> .
    
    ex:person1 a foaf:Person ;
        foaf:name "John Doe" ;
        foaf:age 30 .
    
    ex:person2 a foaf:Person ;
        foaf:name "Jane Smith" ;
        foaf:age 25 .
    """
    
    rdf_file = tmp_path / "sample.ttl"
    rdf_file.write_text(rdf_content)
    return rdf_file
```

This technical appendix provides the detailed implementation specifics needed to realize the integration described in the main analysis report.
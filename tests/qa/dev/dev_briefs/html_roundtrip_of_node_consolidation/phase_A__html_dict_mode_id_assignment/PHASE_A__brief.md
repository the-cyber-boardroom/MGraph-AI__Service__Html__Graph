# Phase A: Html_Dict Node_Id Assignment

**Status**: 🚧 In Progress  
**Depends On**: Html__To__Html_Dict (existing parser) ✅

---

## Objective

> Assign unique `node_id` to every element and text node at the Html_Dict parsing level, enabling source tracking across the entire transformation pipeline.

---

## The Solution

Create `Html__To__Html_Dict__With__Node_Ids` as a subclass of `Html__To__Html_Dict`:

```python
class Html__To__Html_Dict__With__Node_Ids(Html__To__Html_Dict):
    
    def handle_starttag(self, tag, attrs):
        super().handle_starttag(tag, attrs)
        # Add node_id to newly created tag
        
    def handle_data(self, data):
        super().handle_data(data)
        # Add node_id to text node if one was created
        
    def generate_node_id(self) -> str:
        return str(Obj_Id())
```

---

## Output Format

```python
# Input HTML:
"<div class='container'>Hello <b>World</b></div>"

# Output from Html__To__Html_Dict (current - no node_ids):
{
    'tag'  : 'div',
    'attrs': {'class': 'container'},
    'nodes': [
        {'type': 'TEXT', 'data': 'Hello '},
        {'tag': 'b', 'attrs': {}, 'nodes': [
            {'type': 'TEXT', 'data': 'World'}
        ]}
    ]
}

# Output from Html__To__Html_Dict__With__Node_Ids (new - with node_ids):
{
    'tag'    : 'div',
    'attrs'  : {'class': 'container'},
    'node_id': 'a1b2c3',                                  # NEW
    'nodes'  : [
        {'type': 'TEXT', 'data': 'Hello ', 'node_id': 'd4e5f6'},    # NEW
        {'tag': 'b', 'attrs': {}, 'node_id': 'g7h8i9', 'nodes': [   # NEW
            {'type': 'TEXT', 'data': 'World', 'node_id': 'j0k1l2'}  # NEW
        ]}
    ]
}
```

---

## Implementation Details

### handle_starttag Override

```python
def handle_starttag(self, tag, attrs):
    super().handle_starttag(tag, attrs)                             # Let parent create the tag
    
    if tag.lower() not in self.void_elements:
        self.current['node_id'] = self.generate_node_id()           # self.current IS the new tag
    else:
        # Void elements: tag appended to parent's nodes, self.current unchanged
        self.current[STRING__SCHEMA_NODES][-1]['node_id'] = self.generate_node_id()
```

### handle_data Override

```python
def handle_data(self, data):
    super().handle_data(data)                                       # Let parent create text node
    
    if data.strip():                                                # Same condition as parent
        self.current[STRING__SCHEMA_NODES][-1]['node_id'] = self.generate_node_id()
```

---

## Files to Create

| File | Purpose |
|------|---------|
| `Html__To__Html_Dict__With__Node_Ids.py` | New subclass with node_id assignment |
| `test_Html__To__Html_Dict__With__Node_Ids.py` | Tests for node_id assignment |

---

## Test Cases

### Test A.1: Basic Node_Id Assignment

```python
def test_convert__with_node_ids(self):
    html = "<p>Hello</p>"
    with Html__To__Html_Dict__With__Node_Ids(html) as _:
        result = _.convert()
        
        assert 'node_id' in result                                  # Element has node_id
        assert 'node_id' in result['nodes'][0]                      # Text node has node_id
        assert result['node_id'] != result['nodes'][0]['node_id']   # Different IDs
```

### Test A.2: Void Elements Get Node_Ids

```python
def test_convert__void_elements_have_node_ids(self):
    html = "<p>Before<br>After</p>"
    with Html__To__Html_Dict__With__Node_Ids(html) as _:
        result = _.convert()
        
        assert 'node_id' in result['nodes'][1]                      # <br> has node_id
        assert result['nodes'][1]['tag'] == 'br'
```

### Test A.3: All Nodes Have Unique Node_Ids

```python
def test_convert__all_node_ids_unique(self):
    html = "<div><p>A</p><p>B</p><p>C</p></div>"
    with Html__To__Html_Dict__With__Node_Ids(html) as _:
        result   = _.convert()
        node_ids = collect_all_node_ids(result)
        
        assert len(node_ids) == len(set(node_ids))                  # All unique
```

### Test A.4: Backward Compatible Structure

```python
def test_convert__backward_compatible(self):
    html = "<div>Hello</div>"
    
    result_old = Html__To__Html_Dict(html).convert()
    result_new = Html__To__Html_Dict__With__Node_Ids(html).convert()
    
    # Structure identical except for node_id fields
    assert result_old['tag']   == result_new['tag']
    assert result_old['attrs'] == result_new['attrs']
    assert len(result_old['nodes']) == len(result_new['nodes'])
```

---

## Next Steps After Phase A

1. **Phase B**: Modify `Html__To__Html_MGraph__Document` to reuse node_ids from dict
2. **Phase C**: Track source node_ids in `Html_Use_Case__3` transformations
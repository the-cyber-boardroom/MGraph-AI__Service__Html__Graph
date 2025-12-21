# refactor into separate schema files
from typing                                                             import Dict, Any, Optional, List
from osbot_utils.type_safe.Type_Safe                                    import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Node_Id       import Node_Id


# ═══════════════════════════════════════════════════════════════════════════════
# Base Graph Stats Schema
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__Html_MGraph__Stats__Base(Type_Safe):                              # Stats for base graph
    total_nodes : int     = 0
    total_edges : int     = 0
    root_id     : Node_Id = None


# ═══════════════════════════════════════════════════════════════════════════════
# Component Graph Stats Schemas
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__Html_MGraph__Stats__Head(Schema__Html_MGraph__Stats__Base):       # Stats for head graph
    element_nodes : int = 0
    text_nodes    : int = 0


class Schema__Html_MGraph__Stats__Body(Schema__Html_MGraph__Stats__Base):       # Stats for body graph
    element_nodes : int = 0
    text_nodes    : int = 0


class Schema__Html_MGraph__Stats__Attributes(Schema__Html_MGraph__Stats__Base): # Stats for attributes graph
    registered_elements : int = 0
    total_attributes    : int = 0
    unique_tags         : int = 0


class Schema__Html_MGraph__Stats__Scripts(Schema__Html_MGraph__Stats__Base):    # Stats for scripts graph
    total_scripts    : int = 0
    inline_scripts   : int = 0
    external_scripts : int = 0


class Schema__Html_MGraph__Stats__Styles(Schema__Html_MGraph__Stats__Base):     # Stats for styles graph
    total_styles    : int = 0
    inline_styles   : int = 0
    external_styles : int = 0


# ═══════════════════════════════════════════════════════════════════════════════
# Document Stats Schema
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__Html_MGraph__Stats__Document(Type_Safe):                          # Combined stats for entire document
    document   : Schema__Html_MGraph__Stats__Base       = None
    head       : Schema__Html_MGraph__Stats__Head       = None
    body       : Schema__Html_MGraph__Stats__Body       = None
    attributes : Schema__Html_MGraph__Stats__Attributes = None
    scripts    : Schema__Html_MGraph__Stats__Scripts    = None
    styles     : Schema__Html_MGraph__Stats__Styles     = None


# ═══════════════════════════════════════════════════════════════════════════════
# JSON Export Schemas
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__Html_MGraph__Json__Base(Type_Safe):                               # JSON export for base graph
    nodes   : Dict[str, Any] = None
    edges   : Dict[str, Any] = None
    root_id : str            = None


class Schema__Html_MGraph__Json__Document(Type_Safe):                           # JSON export for entire document
    document   : Dict[str, Any] = None
    head       : Dict[str, Any] = None
    body       : Dict[str, Any] = None
    attributes : Dict[str, Any] = None
    scripts    : Dict[str, Any] = None
    styles     : Dict[str, Any] = None


# ═══════════════════════════════════════════════════════════════════════════════
# Element Info Schema
# ═══════════════════════════════════════════════════════════════════════════════

class Schema__Html_MGraph__Element_Info(Type_Safe):                             # Comprehensive element information
    node_id        : Node_Id         = None
    tag            : str             = None
    attrs          : Dict[str, str]  = None
    in_head        : bool            = False
    in_body        : bool            = False
    script_content : str             = None
    style_content  : str             = None
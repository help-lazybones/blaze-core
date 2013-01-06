
# blaze/datashape/dyacc.py
# This file is automatically generated. Do not edit.
_tabversion = '3.2'

_lr_method = 'LALR'

_lr_signature = '@0\x12\xb0\xec\xe3\xab:\x9cU\x9cqU\x16\xa7\x8a'
    
_lr_action_items = {'LBRACE':([0,2,3,5,6,7,8,9,11,16,17,20,21,22,25,28,31,34,35,],[1,-6,-12,-4,-13,-10,-9,-11,1,1,1,-4,1,-16,-14,1,1,-15,-5,]),'NAME':([0,1,2,3,5,6,7,8,9,10,11,16,17,18,19,20,21,22,23,24,25,27,28,31,34,35,],[3,15,-6,-12,-4,-13,-10,-9,-11,19,3,3,3,19,-8,-4,3,-16,15,30,-14,19,3,3,-15,-5,]),'SEMI':([1,12,13,14,23,29,30,32,33,37,],[-24,23,-18,-19,-24,23,-21,-23,-22,-20,]),')':([3,6,7,8,9,22,25,26,34,36,],[-12,-13,-10,-9,-11,-16,-14,34,-15,37,]),'(':([3,24,],[17,31,]),'NUMBER':([0,2,3,5,6,7,8,9,11,16,17,20,21,22,24,25,28,31,34,35,],[6,-6,-12,-4,-13,-10,-9,-11,6,6,6,-4,6,-16,32,-14,6,6,-15,-5,]),'EQUALS':([18,19,27,],[28,-8,-7,]),'COMMA':([2,3,6,7,8,9,22,25,26,34,35,36,],[16,-12,-13,-10,-9,-11,-16,16,16,-15,16,16,]),'COLON':([15,],[24,]),'BIT':([0,2,3,5,6,7,8,9,11,16,17,20,21,22,24,25,28,31,34,35,],[9,-6,-12,-4,-13,-10,-9,-11,9,9,9,-4,9,-16,33,-14,9,9,-15,-5,]),'$end':([2,3,4,5,6,7,8,9,11,20,21,22,25,34,35,],[-6,-12,0,-2,-13,-10,-9,-11,-1,-4,-3,-16,-14,-15,-5,]),'TYPE':([0,2,3,5,6,7,8,9,11,20,21,22,25,34,35,],[10,-6,-12,-4,-13,-10,-9,-11,10,-4,10,-16,-14,-15,-5,]),'RBRACE':([1,12,13,14,23,29,30,32,33,37,],[-24,22,-18,-19,-24,-17,-21,-23,-22,-20,]),}

_lr_action = { }
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = { }
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'rhs_expression':([0,11,16,17,21,28,31,],[2,2,25,26,2,35,36,]),'record_opt':([1,23,],[12,29,]),'top':([0,],[4,]),'stmt':([0,11,21,],[5,20,20,]),'record':([0,11,16,17,21,28,31,],[7,7,7,7,7,7,7,]),'appl':([0,11,16,17,21,28,31,],[8,8,8,8,8,8,8,]),'record_item':([1,23,],[13,13,]),'lhs_expression':([10,18,27,],[18,27,27,]),'empty':([1,23,],[14,14,]),'mod':([0,11,21,],[11,21,21,]),}

_lr_goto = { }
for _k, _v in _lr_goto_items.items():
   for _x,_y in zip(_v[0],_v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = { }
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> top","S'",1,None,None,None),
  ('top -> mod','top',1,'p_top','',154),
  ('top -> stmt','top',1,'p_top','',155),
  ('mod -> mod mod','mod',2,'p_decl1','',160),
  ('mod -> stmt','mod',1,'p_decl2','',164),
  ('stmt -> TYPE lhs_expression EQUALS rhs_expression','stmt',4,'p_statement_assign','',168),
  ('stmt -> rhs_expression','stmt',1,'p_statement_expr','',186),
  ('lhs_expression -> lhs_expression lhs_expression','lhs_expression',2,'p_lhs_expression','',192),
  ('lhs_expression -> NAME','lhs_expression',1,'p_lhs_expression_node','',197),
  ('rhs_expression -> appl','rhs_expression',1,'p_rhs_expression_node1','',203),
  ('rhs_expression -> record','rhs_expression',1,'p_rhs_expression_node1','',204),
  ('rhs_expression -> BIT','rhs_expression',1,'p_rhs_expression_node2','',208),
  ('rhs_expression -> NAME','rhs_expression',1,'p_rhs_expression_node3','',212),
  ('rhs_expression -> NUMBER','rhs_expression',1,'p_rhs_expression_node3','',213),
  ('rhs_expression -> rhs_expression COMMA rhs_expression','rhs_expression',3,'p_rhs_expression','',217),
  ('appl -> NAME ( rhs_expression )','appl',4,'p_appl','',224),
  ('record -> LBRACE record_opt RBRACE','record',3,'p_record','',228),
  ('record_opt -> record_opt SEMI record_opt','record_opt',3,'p_record_opt1','',236),
  ('record_opt -> record_item','record_opt',1,'p_record_opt2','',243),
  ('record_opt -> empty','record_opt',1,'p_record_opt3','',247),
  ('record_item -> NAME COLON ( rhs_expression )','record_item',5,'p_record_item1','',251),
  ('record_item -> NAME COLON NAME','record_item',3,'p_record_item2','',255),
  ('record_item -> NAME COLON BIT','record_item',3,'p_record_item2','',256),
  ('record_item -> NAME COLON NUMBER','record_item',3,'p_record_item2','',257),
  ('empty -> <empty>','empty',0,'p_empty','X',261),
]

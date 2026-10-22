<?php
function startForm(string $action,array $hidden=[],string $class=''): void { global $page;
 echo '<form method="post" class="'.h($class).'">';
 $all=['csrf'=>$_SESSION['csrf'],'action'=>$action,'back'=>url($_GET?:['page'=>$page]),...$hidden];foreach($all as $k=>$v)echo '<input type="hidden" name="'.h($k).'" value="'.h($v).'">';
}
function selectField(string $name,string $label,array $options,mixed $selected='',bool $optional=false): void {
 echo '<label>'.h($label).'<select name="'.h($name).'"'.($optional?'':' required').'>';
 echo '<option value="">'.($optional?'Tous / aucun':'Choisir…').'</option>';
 foreach($options as $opt)echo '<option value="'.h($opt['id']).'"'.((string)$opt['id']===(string)$selected?' selected':'').'>'.h($opt['label']).'</option>';echo '</select></label>';
}
function inputField(string $name,string $label,mixed $value='',string $type='text',bool $required=true): void {
 echo '<label>'.h($label).'<input type="'.h($type).'" name="'.h($name).'" value="'.h($value).'"'.($required?' required':'').($type==='number'?' step="any"':'').'></label>';
}
function badge(mixed $value): string { return '<span class="badge '.h((string)$value).'">'.h(Catalog::VALUES[(string)$value]??$value).'</span>'; }
function dataTable(array $rows,array $heads=[]): void {
 if(!$rows){echo '<p class="empty">Aucun résultat pour ces critères.</p>';return;}
 $keys=$heads?array_keys($heads):array_keys($rows[0]);echo '<div class="table-scroll"><table><thead><tr>';
 foreach($keys as $key)echo '<th scope="col">'.h($heads[$key]??Catalog::LABELS[$key]??str_replace('_',' ',$key)).'</th>';echo '</tr></thead><tbody>';
 foreach($rows as $row){echo '<tr>';foreach($keys as $k){$v=$row[$k]??null;if(in_array($k,['etat','status','role'],true)&&is_string($v))$v=Catalog::VALUES[$v]??$v;if(is_float($v)||(is_string($v)&&preg_match('/^-?\d+\.\d+$/',$v)))$v=rtrim(rtrim(number_format((float)$v,4,',',' '),'0'),',');echo '<td>'.($v===null?'—':h($v)).'</td>';}echo '</tr>';}echo '</tbody></table></div>';
}
function pagination(int $total,int $page): void { $last=max(1,(int)ceil($total/20));echo '<nav class="pagination" aria-label="Pagination"><span>'.h($total).' résultats · Page '.h($page).' sur '.$last.'</span>';if($page>1)echo '<a class="button secondary" href="'.h(url([...$_GET,'p'=>$page-1])).'">Précédent</a>';if($page<$last)echo '<a class="button secondary" href="'.h(url([...$_GET,'p'=>$page+1])).'">Suivant</a>';echo '</nav>'; }
function periodFields(): void {inputField('from','Du',$_GET['from']??date('Y-m-d'),'date');inputField('to','Au',$_GET['to']??($_GET['from']??date('Y-m-d')),'date');}
function filterEnd(string $page): void {echo '<button>Filtrer</button><a href="'.h(url(['page'=>$page])).'">Réinitialiser</a></form>';}
function exportPrint(string $kind): void { global $user;echo '<div class="actions no-print">';if(Auth::can($user,'reports'))echo '<a class="button secondary" href="'.h(url([...$_GET,'page'=>'export','kind'=>$kind])).'">Exporter CSV</a>';echo '<button type="button" class="secondary" data-print>Imprimer l’état</button></div>';}

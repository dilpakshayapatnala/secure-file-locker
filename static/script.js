function toggleView(type){

let table=document.getElementById("tableview")
let grid=document.getElementById("gridview")

if(type=="grid"){
table.style.display="none"
grid.style.display="grid"
}
else{
table.style.display="table"
grid.style.display="none"
}

}

function selectAll(source){

let checkboxes=document.getElementsByName("file")

for(let i=0;i<checkboxes.length;i++){

checkboxes[i].checked=source.checked

}

}

function toggleActions(box){

let actions=box.parentElement.querySelector(".actions")

if(box.checked){
actions.style.display="block"
}
else{
actions.style.display="none"
}

}
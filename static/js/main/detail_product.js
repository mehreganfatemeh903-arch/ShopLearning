function add_review_btn():void{
  const review_div:HTMLElement=document.getElementById(elementId:'review_body')
  const review_btn:HTMLElement=document.getElementById(element:'review_btn')
  if(review_div.classList.contains('d_none')){
     review_btn.innerText='Add Your Review'
  }else{
        review_btn.innerText='Close Review'
  }
}
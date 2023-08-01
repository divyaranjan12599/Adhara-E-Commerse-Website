function loadProductOption(optionId){
  var newUrl = addParamToURL(window.location.href,'option_id',optionId)
  window.location.href=newUrl;
  // return false;
}
function readURL(input,target) {
    if (input.files && input.files[0]) {
      var reader = new FileReader();
      
      reader.onload = function(e) {
        $(target).attr('src', e.target.result);
      }
      reader.readAsDataURL(input.files[0]); // convert to base64 string
    }
  }
  $("input.preview").change(function() {
    readURL(this,$(this).next());
  });


function fillupcitystate(data){
      try{
          var cityoption = "<option selected value='"+data.city_id+"'>"+data.city+"<option>";
          var stateoption = "<option selected value='"+data.state_id+"'>"+data.state+"<option>";
          $('#city').html(cityoption);
          $('#state').html(stateoption);
      }
      catch(err){
          $('#city').html('');
          $('#state').html('');   
      }
  }
  

$('#pincode').on('keyup change',function(e){
var pincode= $(this).val();
if (pincode.length != 6){
  return;
}
var callback = $(this).data('callback');
 $.ajax({
        type: "GET",
        url: "{{ url('api:csbypincode')}}",
        data:"pincode="+pincode,
        success: function(data){
          if (typeof callback !== 'undefined') {
              return window[callback](data)
          }
          else{
            $('#city').val(data.city);
            $('#state').val(data.state);
          }
        },
        error: function(data){
              console.log("Internal Server Error");
          
        },
        dataType: 'json'
      });
});



	
function addParamToURL(loc,param,val){
	var url = new URL(loc);
	var query_string = url.search;
	var search_params = new URLSearchParams(query_string);
	search_params.set(param, val);
	url.search = search_params.toString();
	var new_url = url.toString();
	return new_url;
}
function loadProductOption(optionId){
	var newUrl = addParamToURL(window.location.href,'option_id',optionId)
	window.location.href=newUrl;
	return false;
}

function cartApi(formData){
    
	$.ajax({
		url: add_to_cart_url,
		type: 'POST',
		data: formData,
		success: function (data) {
			alert(data);
			parent.location.reload(true);
			// window.location.hre?f = window.location.href;
			return false;
		},
		error: function (xhr, ajaxOptions, thrownError) {
		
			if(xhr.status==403) {
				if(confirm("You must be logged in, proceed?")){
				var newUrl = loginurl + "?next=" + window.location.href
				window.location.href = newUrl;
				}
			}
			if(xhr.status==400) {
				alert("The Product Cannot Be Added at the moment.");
			}
		},
		cache: false,
	});
	return false;
}
function wishlistApi(formData){
	$.ajax({
		url: wlcurl,
		type: 'POST',
		data: formData,
		success: function (data) {
			alert(data);
			// parent.location.reload(true);
			// window.location.hre?f = window.location.href;
			window.location.reload()
		},
		error: function (xhr, ajaxOptions, thrownError) {
			if(xhr.status==403) {
				if(confirm("You must be logged in, proceed?")){
				var newUrl = loginurl + "?next=" + window.location.href
				window.location.href = newUrl;
				}
			}
			if(xhr.status==400) {
				alert("The Product Cannot Be Added to Wishlist at the moment.");
			}
		},
		cache: false,
	});
	return false;
}
function addToCartFn(ele){
	console.log($(ele).val());
	var productId= $(ele).data('product-id');
	var productOptionId= $(ele).data('product-option-id');
	var quantity = 1;
	if( $('#qty' + productOptionId).length ){
	quantity = $('#qty' + productOptionId).val();
	}
	var formData = "product_id="+productId+"&product_option_id="+productOptionId+"&quantity="+quantity;
	// formData = JSON.stringify( { "product_id": productId, "product_option_id": productOptionId, "quantity": quantity} )
	
	cartApi(formData);
}
$('.addtocart').on('click',function(){
addToCartFn(this);
});

    /* ---------------------------------------------------------------------------- */
    //$( window ).on( "load", function() {
//		document.onkeydown = function(e) {
//			if(e.keyCode == 123) {
//			 return false;
//			}
//			if(e.ctrlKey && e.shiftKey && e.keyCode == 'I'.charCodeAt(0)){
//			 return false;
//			}
//			if(e.ctrlKey && e.shiftKey && e.keyCode == 'J'.charCodeAt(0)){
//			 return false;
//			}
//			if(e.ctrlKey && e.keyCode == 'U'.charCodeAt(0)){
//			 return false;
//			}
//		
//			if(e.ctrlKey && e.shiftKey && e.keyCode == 'C'.charCodeAt(0)){
//			 return false;
//			}      
//		 };
//		 
//		$("html").on("contextmenu",function(){
//			return false;
//		});
//	});
	
$('.removefromcart').on('click',function(){
	var productId= $(this).data('product-id');
	var productOptionId= $(this).data('product-option-id');
	var quantity = 0;
	var formData = "product_id="+productId+"&product_option_id="+productOptionId+"&quantity="+quantity;
	// formData = JSON.stringify( { "product_id": productId, "product_option_id": productOptionId, "quantity": quantity} )
	cartApi(formData);
});



function editWishlist(ele,action){
	var productOptionId= $(ele).data('product-option-id');
	var formData = "product_option_id="+productOptionId;
	if(action=="delete"){
		formData += "&delete=yes"
	}
	// formData = JSON.stringify( { "product_id": productId, "product_option_id": productOptionId, "quantity": quantity} )
	wishlistApi(formData);

}
$('.addtowishlist').on('click',function(){
	editWishlist(this,'add');
});

$('.removefromwishlist').on('click',function(){
	editWishlist(this,'delete');
});


    $(document).ready(function(){

var list = $("#colorfilter li");
var numToShow = 5;
var button = $("#next");
var numInList = list.length;
list.hide();
if (numInList > numToShow) {
  button.show();
}
list.slice(0, numToShow).show();

button.click(function(){
    var showing = list.filter(':visible').length;
    list.slice( numToShow).fadeIn();
    var nowShowing = list.filter(':visible').length;
    if (nowShowing >= numInList) {
      button.hide();
    }
});

});



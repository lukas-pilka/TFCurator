// sharing window
let splash = document.getElementById("sharingPopup"); // Get a reference to the sharing window
let container = document.getElementById("container");
let mainMenu = document.getElementById("mainMenu");

function closeWindow() {
	let element = document.getElementById("sharingPopup");
	element.classList.toggle("closed"); // add class closed
	let d = new Date();
	let xDays = 1 // * Duration in days
	d.setTime(d.getTime() + (xDays * 24 * 60 * 60 * 1000));
	let expires = "expires=" + d.toGMTString();
	document.cookie = "visited=true;" + expires; // Creating cookie when closing window
	container.classList.toggle("blurred");
	mainMenu.classList.toggle("blurred");
}
window.addEventListener("load", function () {
	if (document.cookie.indexOf("visited=true") === -1) { // Check to see if the cookie indicates a first-time visit
		setTimeout(function () { // Reveal the window after delay
			splash.classList.remove("closed");
			container.classList.toggle("blurred");
			mainMenu.classList.toggle("blurred");
		}, 20000); // set delay in ms
	}
});

// get urls for sharing

window.onload = function() {
	let fbLink = document.getElementsByClassName("jsFbShare");
	let fb;
	for (fb = 0; fb < fbLink.length; fb++) {
	  fbLink[fb].href ='http://www.facebook.com/share.php?u=' + encodeURIComponent(location.href);
	}
	let twLink = document.getElementsByClassName("jsTwShare");
	let tw;
	for (tw = 0; tw < twLink.length; tw++) {
	  twLink[tw].href ='https://twitter.com/share?url=' + encodeURIComponent(location.href);
	}
}

// menu window

function openMenu() {
  let element = document.getElementById("menuSecondLevel");
  element.classList.toggle("opened");
  let element2 = document.getElementById("container");
  element2.classList.toggle("blurred");
  let menuClosingField = document.getElementById("menuCover");
  menuClosingField.classList.toggle("hidden");
  let element3 = document.getElementById("jsMenuIcon");
  element3.classList.toggle("opened");
  let element4 = document.getElementById("jsSearchWindow");
  element4.classList.remove("opened");
  let element5 = document.getElementById("jsShowcase");
  element5.classList.remove("opened");
  let element6 = document.getElementById("jsAboutWindow");
  element6.classList.remove("opened");
}
function openSearch() {
  let element = document.getElementById("jsSearchWindow");
  element.classList.toggle("opened");
  let element2 = document.getElementById("jsMenuWindow");
  element2.classList.toggle("opened");
}
function openShowcase() {
  let element = document.getElementById("jsShowcase");
  element.classList.toggle("opened");
  let element2 = document.getElementById("jsMenuWindow");
  element2.classList.toggle("opened");
}
function openAbout() {
  let element = document.getElementById("jsAboutWindow");
  element.classList.toggle("opened");
  let element2 = document.getElementById("jsMenuWindow");
  element2.classList.toggle("opened");
}

// Open popup window with search forms if contains error messages

function checkErrors() {
	let isError = document.getElementsByClassName('errorMessage');
	if (isError.length > 0) {
		openMenu()
		openSearch()
	}
}
checkErrors()

// Show select for object comparison

function showComparisonSelect() {
  // Get the checkbox
  var checkBox = document.getElementById("comparisonCheck");
  // Get the output text
  var text = document.getElementById("comparisonClassBox");

  // If the checkbox is checked, display the output text
  if (checkBox.checked == true){
    text.classList.add("opened");
  } else {
    text.classList.remove("opened");
  }
}

// Copy url

function copyUrl() {
	if (!window.getSelection) {
		alert('Please copy the URL from the location bar.');
		return;
	}
	const dummy = document.createElement('p');
	dummy.textContent = window.location.href;
	document.body.appendChild(dummy);

	const range = document.createRange();
	range.setStartBefore(dummy);
	range.setEndAfter(dummy);

	const selection = window.getSelection();
	// First clear, in case the user already selected some other text
	selection.removeAllRanges();
	selection.addRange(range);

	document.execCommand('copy');
	document.body.removeChild(dummy);

	let htmlElement = document.getElementsByClassName("jsCopyLink");
	let i;
	for (i = 0; i < htmlElement.length; i++) {
	  htmlElement[i].classList.add("done");
	}
}

// artwork focused

(function(){
	function hasClass(el, cls) {
		if (el.className.match('(?:^|\\s)'+cls+'(?!\\S)')) { return true; }
		}
	function addClass(el, cls) {
		if (!el.className.match('(?:^|\\s)'+cls+'(?!\\S)')) { el.className += ' '+cls; }
		}
	function delClass(el, cls) {
		el.className = el.className.replace(new RegExp('(?:^|\\s)'+cls+'(?!\\S)'),'');
		}


	function elementFromLeft(elem, classToAdd, distanceFromLeft, unit) {
		let container = document.getElementById("container");
		let winX = container.innerWidth || document.documentElement.clientWidth,
		elemLength = elem.length, distLeft, distPercent, distPixels, distUnit, i;
		for (i = 0; i < elemLength; ++i) {
			distLeft = elem[i].getBoundingClientRect().left;
			distPercent = Math.round((distLeft / winX) * 100);
			distPixels = Math.round(distLeft);
			distUnit = unit == 'percent' ? distPercent : distPixels;
			if (distUnit <= distanceFromLeft) {
				if (!hasClass(elem[i], classToAdd)) { addClass(elem[i], classToAdd); }
				} else {
				delClass(elem[i], classToAdd);
				}
			}
		}

	function elementFromTop(elem, classToAdd, distanceFromTop, unit) {
		let container = document.getElementById("container");
		let winY = container.innerHeight || document.documentElement.clientHeight,
		elemLength = elem.length, distTop, distPercent, distPixels, distUnit, i;
		for (i = 0; i < elemLength; ++i) {
			distTop = elem[i].getBoundingClientRect().top;
			distPercent = Math.round((distTop / winY) * 100);
			distPixels = Math.round(distTop);
			distUnit = unit == 'percent' ? distPercent : distPixels;
			if (distUnit <= distanceFromTop) {
				if (!hasClass(elem[i], classToAdd)) { addClass(elem[i], classToAdd); }
				} else {
				delClass(elem[i], classToAdd);
				}
			}
		}
	// params: element, classes to add, distance from top, unit ('percent' or 'pixels')

	if(container.innerWidth <= 960) {
		container.addEventListener('scroll', function () {
			elementFromTop(document.querySelectorAll('.artwork'), 'focuseIn', 50, 'percent'); // as top of element hits top of viewport
			elementFromTop(document.querySelectorAll('.artwork'), 'focuseOut', 30, 'percent'); // as top of element hits top of viewport
		}, false);
		container.addEventListener('resize', function () {
			elementFromTop(document.querySelectorAll('.artwork'), 'focuseIn', 50, 'percent'); // as top of element hits top of viewport
			elementFromTop(document.querySelectorAll('.artwork'), 'focuseOut', 30, 'percent'); // as top of element hits top of viewport
		}, false);
	}else{
		container.addEventListener('scroll', function () {
			elementFromLeft(document.querySelectorAll('.artwork'), 'focuseIn', 50, 'percent'); // as left of element hits left of viewport
			elementFromLeft(document.querySelectorAll('.artwork'), 'focuseOut', 30, 'percent'); // as left of element hits left of viewport
		}, false);
		container.addEventListener('resize', function () {
			elementFromLeft(document.querySelectorAll('.artwork'), 'focuseIn', 50, 'percent'); // as left of element hits left of viewport
			elementFromLeft(document.querySelectorAll('.artwork'), 'focuseOut', 30, 'percent'); // as left of element hits left of viewport
		}, false);
	}

})();


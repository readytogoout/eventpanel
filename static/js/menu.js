'use strict';
(function () {
    const headerNavigationToggleElement = document.getElementById("navigation-toggle");
    const headerNavigationContentContainerElement = document.getElementById("navigation-container");
    const navigationExpandedClassName = "navigation-collapsed";
    headerNavigationToggleElement.addEventListener("click", function (ev) {
        if (headerNavigationContentContainerElement.classList.contains(navigationExpandedClassName)) {
            headerNavigationContentContainerElement.classList.remove(navigationExpandedClassName);
        } else {
            headerNavigationContentContainerElement.classList.add(navigationExpandedClassName);
        }
        ev.preventDefault();
    });
})();
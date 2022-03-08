import ReactDOM from "react-dom";
import React from "react";
import { Provider } from "react-redux";
import store from "@apps/shared/reduxAppStore";
import CartNavLink from "./CartNavLink";

// Initialise the cart icon on the page, if cart app is enabled.
window.addEventListener("load", () => {
    if (document.getElementById("cart-page-link")) {
        ReactDOM.render(
            (<Provider store={store}>
                <CartNavLink />
            </Provider>),
            document.getElementById("cart-page-link")
        );
    }
});

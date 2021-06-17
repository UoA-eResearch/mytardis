import React, { useCallback } from "react";
import ReactDOM from "react-dom";
import "./cart.css";
import Button from "react-bootstrap/Button";
import { BsTrash } from "react-icons/bs";
import { Provider, useDispatch } from "react-redux";
import { BrowserRouter, HashRouter, Link, Route, Switch } from "react-router-dom";
import store from "@apps/shared/reduxAppStore";
import { removeAllItems } from "./cartSlice";
import CartItemList from "./CartItemList";
import "bootstrap/dist/css/bootstrap.css";
import TransferScreen from "./TransferScreen";

export const CartScreen = (props) => {
    const dispatch = useDispatch();
    const handleRemoveAll = useCallback(
        () => {
            dispatch(removeAllItems());
        },
        [dispatch, removeAllItems]);
    return <div>
        <h1 className="h3 my-3">Cart</h1>
        <section className="cart-summary">
            <p>Total size: 41.5GB</p>
            <div className="cart-summary__actions">
                <Link to="/transfer" className="btn btn-primary">Transfer to an endpoint</Link>
                <Button variant="secondary">Download</Button>
                <Button variant="secondary">Get manifest</Button>
            </div>
        </section>
        <section>
            <CartItemList />
            <p><button className="btn btn-outline-secondary" onClick={handleRemoveAll} variant=""><BsTrash /> Remove all</button></p>

        </section>

    </div>;
};



ReactDOM.render(
    <HashRouter>
        <Provider store={store}>
            <div className="container">
                <main className="cart-content shadow-sm">
                    <Switch>
                        <Route path="/transfer">
                            <TransferScreen />
                        </Route>
                        <Route path="/">
                            <CartScreen />
                        </Route>
                    </Switch>
                </main>
            </div>      
        </Provider>
    </HashRouter>,
    document.getElementById("cart-app"),
);
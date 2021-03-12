import React, { useEffect } from "react";
import ReactDOM from "react-dom";
import "./cart.css";
import Button from "react-bootstrap/Button";
import Dropdown from "react-bootstrap/Dropdown";
import DropdownButton from "react-bootstrap/DropdownButton";
import { BsTrash, BsDownload } from "react-icons/bs";
import { Provider, useDispatch, useSelector } from "react-redux";
import store from "./store";
import { initialiseSlice } from "./cartSlice";
import CartItemList from "./CartItemList";

const CartScreen = (props) => {
    const dispatch = useDispatch();
    useEffect(() => {
        dispatch(initialiseSlice());
    }, [dispatch]);
    return <div className="cart-page container">
        <h1 className="h3 my-3">Cart</h1>
        <main className="cart-page-content shadow-sm">
            <section className="mb-">
                <h2>Download options</h2>
                <p>Total download size: 41.5GB</p>
                <div className="cart__actions">
                    <Button variant="primary"><BsDownload /> Download</Button>
                    <Button variant="secondary">Get Manifest</Button>
                    <DropdownButton variant="secondary" title="Push to..." className="d-inline-block">
                        <Dropdown.Item>NeSI</Dropdown.Item>
                        <Dropdown.Item>Nectar</Dropdown.Item>
                    </DropdownButton>
                </div>
                {/* <Form.Control type="text" placeholder="Filter by name"/> */}
            </section>
            <section>
                {/* <h2>Objects to be downloaded</h2> */}
                <CartItemList />
                <hr />
                <p className="summary">104 Datafiles from 4 Projects, 7 Experiments and 10 Datasets.</p>
                <p><Button variant="outline-danger"><BsTrash /> Remove all</Button></p>

            </section>

        </main>
    </div>;
};

ReactDOM.render(
    <Provider store={store}>
        <CartScreen />
    </Provider>,
    document.getElementById("cart-app"),
);
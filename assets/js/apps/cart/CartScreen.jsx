import React, { useCallback } from "react";
import { removeAllItems } from "./cartSlice";
import CartItemList from "./CartItemList";
import Button from "react-bootstrap/Button";
import { BsTrash } from "react-icons/bs";
import { useDispatch } from "react-redux";
import { Link } from "react-router-dom";


const CartScreen = (props) => {
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

export default CartScreen;
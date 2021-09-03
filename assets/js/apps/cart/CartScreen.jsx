import React, { useCallback } from "react";
import { removeAllItems } from "./cartSlice";
import CartItemList from "./CartItemList";
import Button from "react-bootstrap/Button";
import { BsTrash } from "react-icons/bs";
import { useDispatch, useSelector } from "react-redux";
import { Link } from "react-router-dom";
import { useGetTotalSizeQuery } from "../shared/api";
import humanFileSize from "../shared/humanFileSize";

function CartTotalSize() {
    const itemsInCart = useSelector(state => state.cart.itemsInCart.byId);
    const {data: totalSize, isLoading } = useGetTotalSizeQuery(itemsInCart);
    if (isLoading) {
        return <div className="mb-4">
            <div className="spinner-border" role="status">
                <span className="sr-only">Loading...</span>
            </div>
        </div>;
    }
    return <div className="mb-4">Total size: <span>{humanFileSize(totalSize)}</span></div>;
} 

const CartScreen = (props) => {
    const dispatch = useDispatch();
    const handleRemoveAll = useCallback(
        () => {
            dispatch(removeAllItems());
        },
        [dispatch, removeAllItems]);
    return <div>
        <h1 className="my-3">Cart</h1>
        <section className="cart-summary">
            <CartTotalSize />
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
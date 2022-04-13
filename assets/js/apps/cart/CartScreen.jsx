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

function DownloadLink({isLargeDownload}) {
    if (isLargeDownload) {
        // If it's a large download, show redirect to download request page instead.
        return <Link to="/download" className="btn btn-secondary">Download</Link>;
    } else {
        return <a className="btn btn-secondary" href="/api/v1/download-small">Download</a>;
    }
}

function CartSummary(props) {
    const itemsInCart = useSelector(state => state.cart.itemsInCart.byId);
    const {data: totalSize, isLoading } = useGetTotalSizeQuery(itemsInCart);
    if (isLoading) {
        return <section className="cart-summary">
            <div className="mb-4">
                <div className="spinner-border" role="status">
                    <span className="sr-only">Loading...</span>
                </div>
            </div>
        </section>;
    }
    // If size of download is larger than 5GiB.
    const isLargeDownload = totalSize > 5368709120;
    return <section className="cart-summary">
        <div className="mb-4">Total size: <span>{humanFileSize(totalSize)}</span></div>
        <div className="cart-summary__actions">
            <Link to="/transfer" className="btn btn-primary">Transfer to a Globus endpoint</Link>
            <DownloadLink isLargeDownload={isLargeDownload} />
            <Button variant="secondary">Get manifest</Button>
        </div>
    </section>
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
        <CartSummary />
        <section>
            <CartItemList />
            <p><button className="btn btn-outline-secondary" onClick={handleRemoveAll} variant=""><BsTrash /> Remove all</button></p>

        </section>

    </div>;
};

export default CartScreen;

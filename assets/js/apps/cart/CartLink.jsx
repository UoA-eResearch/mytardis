import React, { useCallback } from "react";
import { useEffect } from "react";
import { Badge, Button, Popover, OverlayTrigger, PopoverContent, PopoverTitle } from "react-bootstrap";
import { FaShoppingCart } from "react-icons/fa";
import { useSelector, useDispatch } from "react-redux";
import { notificationDismissed, initialiseSlice, NOTIFICATION_TYPE } from "./cartSlice";

const itemAddedNotification = (onDismiss) => (
    <Popover id="cart-item-added">
        <PopoverTitle as="h3">Items added to download list.</PopoverTitle>
        <PopoverContent>
                Go to the Cart tab to see what’s in your list and download them.
            <Button onClick={onDismiss}>OK, Got It.</Button>
        </PopoverContent>
    </Popover>
);

const itemRemovedNotification = (onDismiss) => (
    <Popover id="cart-item-removed">
        <PopoverTitle as="h3">Item removed from download list.</PopoverTitle>
        <PopoverContent>
                Go to the Cart tab to see what’s in your list and download them.
            <Button onClick={onDismiss}>OK, Got It</Button>
        </PopoverContent>
    </Popover>
);

export default function CartLink(props) {
    const dispatch = useDispatch();
    useEffect(() => {
        dispatch(initialiseSlice(false));
    }, [dispatch]);
    const numberOfItems = useSelector(state => {
        const items = state.cart.itemsInCart;
        if (!items || !items.allIds) {
            return undefined;
        }
        // Get the length of each array of items, then add them together.
        return items.allIds
            .map(itemId => (items.byId[itemId].length))
            .reduce((previous, current) => previous + current, 0);
    });

    const toggleNotification = useCallback(
        () => {
            dispatch(notificationDismissed());
        },
        [dispatch, notificationDismissed],
    );

    const hasNotification = useSelector(state => !!state.cart.activeNotification);
    const activeNotification = useSelector(state => {
        const notification = state.cart.activeNotification;
        if (!notification) {
            return <></>;
        }
        switch (notification) {
            case NOTIFICATION_TYPE.ItemsAdded:
                return itemAddedNotification(toggleNotification);
            case NOTIFICATION_TYPE.ItemsRemoved:
                return itemRemovedNotification(toggleNotification);
            default:
                return <></>;
        }
    });
    // useEffect(() => {
    //     getNumberOfItems().then(numItems => {
    //         setNumOfItems(numItems);
    //     });
    //     const cartIcon = window.cartIcon = {};
    //     cartIcon.itemsAdded = () => {
    //         getNumberOfItems().then(numItems => {
    //             setNumOfItems(numItems);
    //         });
    //     };

    //     cartIcon.itemsRemoved = () => {
    //     };
    //     return () => {
    //         // Remove event listeners.
    //         window.reloadCartItemCount = null;
    //     };
    // }, [getNumberOfItems, setNumOfItems]);

    return (<OverlayTrigger
        show={hasNotification}
        onToggle={toggleNotification}
        placement="bottom"
        overlay={activeNotification}>
        <a className="nav-link" href="/apps/cart">
            <FaShoppingCart />{" "}
                    Cart{" "}
            { numberOfItems !== undefined ? <Badge variant="secondary">{numberOfItems} <span className="sr-only">items in cart</span></Badge> : null }
        </a>
    </OverlayTrigger>
    );

    // return <OverlayTrigger 
    //     // trigger="hover"
    //     // placement="bottom"
    //     // overlay={itemAddedNotification}
    //     overlay={
    //         <Tooltip id="tooltip-no-download">
    //             You can&apos;t download this item.
    //         </Tooltip>
    //     }>
    //     <span>
    //         <a className="nav-link" href="/apps/cart"><FaShoppingCart /> Cart</a>
    //     </span>
    // </OverlayTrigger>;

}
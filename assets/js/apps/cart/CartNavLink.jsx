/*
Component for top navigation cart icon.
*/
import React, { useCallback } from "react";
import { Badge, Button, Popover, OverlayTrigger, PopoverContent, PopoverTitle } from "react-bootstrap";
import { FaShoppingCart } from "react-icons/fa";
import { useSelector, useDispatch } from "react-redux";
import { notificationDismissed, NOTIFICATION_TYPE } from "./cartSlice";
import PropTypes from "prop-types";

function ItemAddedNotification({onDismiss}) {
    return (
        <Popover id="cart-item-added">
            <PopoverTitle as="h3">Items added to download list.</PopoverTitle>
            <PopoverContent>
                <p>Go to the Cart tab to see what’s in your list and download them.</p>
                <Button onClick={onDismiss}>OK, Got It.</Button>
            </PopoverContent>
        </Popover>
    );
}

ItemAddedNotification.propTypes = {
    onDismiss: PropTypes.func.isRequired
};

function ItemRemovedNotification({onDismiss}) {
    return (
        <Popover id="cart-item-removed">
            <PopoverTitle as="h3">Item removed from download list.</PopoverTitle>
            <PopoverContent>
                <p>Go to the Cart tab to see what’s in your list and download them.</p>
                <Button onClick={onDismiss}>OK, Got It</Button>
            </PopoverContent>
        </Popover>
    );
}

ItemRemovedNotification.propTypes = {
    onDismiss: PropTypes.func.isRequired
};

function CartNavLinkText({numberOfItems}) {
    let itemNumBadge = null;
    if (numberOfItems !== undefined) {
        itemNumBadge = (
            <Badge variant="secondary">
                {numberOfItems} 
                <span className="sr-only">items in cart</span>
            </Badge>
        );
    }
    return (
        <a className="nav-link" href="/apps/cart">
            <FaShoppingCart />{" "}Cart{" "}
            {itemNumBadge}
        </a>
    );
}

CartNavLinkText.propTypes = {
    numberOfItems: PropTypes.number.isRequired
};

export default function CartNavLink(props) {
    const dispatch = useDispatch();
    const numberOfItems = useSelector(state => {
        const items = state.cart.itemsInCart;
        if (!items || !items.allIds) {
            return undefined;
        }
        // Get the number of cart items in each object type, then add them together.
        return items.allIds
            .map(itemId => (items.byId[itemId].length))
            .reduce((previous, current) => previous + current, 0);
    });

    const toggleNotification = useCallback(
        () => {
            dispatch(notificationDismissed());
        },
        [dispatch, notificationDismissed]
    );

    const hasNotification = useSelector(state => !!state.cart.activeNotification);
    const activeNotification = useSelector(state => {
        // Uses the cart.activeNotification property to determine
        // if we need to show any notifications.
        const notification = state.cart.activeNotification;
        if (!notification) {
            return <></>;
        }
        switch (notification) {
            case NOTIFICATION_TYPE.ItemsAdded:
                return <ItemAddedNotification onDismiss={toggleNotification} />;
            case NOTIFICATION_TYPE.ItemsRemoved:
                return <ItemRemovedNotification onDismiss={toggleNotification} />;
            default:
                return <></>;
        }
    });
    return (
        <OverlayTrigger
            show={hasNotification}
            onToggle={toggleNotification}
            placement="bottom"
            overlay={activeNotification}>
            <CartNavLinkText numberOfItems={numberOfItems} />
        </OverlayTrigger>
    );
}
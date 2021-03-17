import React, { useState } from "react";
import PropTypes from "prop-types";
import { useSelector, useDispatch } from "react-redux";
import { eachIdHasCorrespondingItem, LOADING_STATE, removeItem } from "./cartSlice";
import Button from "react-bootstrap/Button";

function ProjectCartItem({item}) {
    return <div>
        Project: {item.name}
    </div>;
}

ProjectCartItem.propTypes = {
    item: PropTypes.shape({
        name: PropTypes.string.isRequired,
        size: PropTypes.number
    })
};

function ExperimentCartItem({item}) {
    return <div>
        Experiment: {item.title}
    </div>;
}

ExperimentCartItem.propTypes = {
    item: PropTypes.shape({
        title: PropTypes.string.isRequired,
        size: PropTypes.number
    })
};

function DatasetCartItem({item}) {
    return <div>
        Dataset: {item.description}
    </div>;
}

DatasetCartItem.propTypes = {
    item: PropTypes.shape({
        description: PropTypes.string.isRequired,
        size: PropTypes.number
    })
};

function DatafileCartItem({item}) {
    return <div>
        Datafile: {item.filename}
    </div>;
}

DatafileCartItem.propTypes = {
    item: PropTypes.shape({
        filename: PropTypes.string.isRequired,
        size: PropTypes.number
    })
};

const CART_ITEM_BY_TYPE = {
    project: ProjectCartItem,
    experiment: ExperimentCartItem,
    dataset: DatasetCartItem,
    datafile: DatafileCartItem
};


export default function CartItemList() {
    const dispatch = useDispatch();
    const cartStatus = useSelector(state => state.cart.status);
    const cartItems = useSelector(state => {
        const status = state.cart.status;
        if (status !== LOADING_STATE.Finished && status !== LOADING_STATE.Validating) {
            return {
                allIds: [],
                byId: {}
            };
        }
        const items = state.cart.itemsInCart;
        const objects = state.cart.objects;
        if (!eachIdHasCorrespondingItem(items, objects)) {
            // Check if each id has an item.
            return {
                allIds: [],
                byId: {}
            };
        }
        const objectsInCartByType = {};
        items.allIds.forEach(typeId => {
            objectsInCartByType[typeId] = items.byId[typeId].map(itemId => (
                objects[typeId][itemId]
            ));
        });
        return {
            allIds: items.allIds,
            byId: objectsInCartByType
        };
    });
    return (
        <div>
            {cartStatus === LOADING_STATE.Error &&
                <p>An error occcurred loading your cart.</p>
            }
            {(cartStatus === LOADING_STATE.Validating || cartStatus === LOADING_STATE.Finished) &&
                <div>
                    {cartStatus === LOADING_STATE.Validating && <p>Revalidating...</p>}
                    {
                        cartItems.allIds.flatMap(typeId => (
                            cartItems.byId[typeId].map(item => {
                                const CartItemComponent = CART_ITEM_BY_TYPE[typeId];
                                return <div key={item.id}>
                                    <CartItemComponent item={item} />
                                    <Button onClick={() => {
                                        dispatch(removeItem(typeId, item.id));
                                    }}>Remove
                                    </Button>
                                </div>;    
                            })
                        ))
                    }
                </div>
            }
        </div>
    );
}
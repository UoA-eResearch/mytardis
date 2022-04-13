import { createSlice } from "@reduxjs/toolkit";

export const NOTIFICATION_TYPE = {
    ItemsRemoved: "REMOVED",
    ItemsAdded: "ADDED"
};

const EMPTY_CART = {
    allIds: [],
    byId: {}
};

const localStorageUtils = {
    getItem: key => JSON.parse(localStorage.getItem(key)),
    setItem: (key, value) => localStorage.setItem(key, JSON.stringify(value))
};

function getInitialState() {
    return {
        itemsInCart: localStorageUtils.getItem("itemIdsByType") || EMPTY_CART,
        transferredItems: {},
        activeNotification: null
    };
}

const cartSlice = createSlice({
    name: "cart",
    initialState: getInitialState(),
    reducers: {
        allItemsRemoved: state => {
            state.itemsInCart = EMPTY_CART;
            state.activeNotification = NOTIFICATION_TYPE.ItemsRemoved;
        },
        itemsAdded: (state, {payload: itemList}) => {
            itemList.forEach(({typeId, id}) => {
                // First, create the type object if it doesn't exist already
                if (!state.itemsInCart.byId[typeId]) {
                    state.itemsInCart.byId[typeId] = [];
                    state.itemsInCart.allIds.push(typeId);
                }
                const typeItems = state.itemsInCart.byId[typeId];
                if (typeItems.some(existingId => existingId === id)) {
                    return;
                }
                typeItems.push(id);
            });
            state.activeNotification = NOTIFICATION_TYPE.ItemsAdded;
        },
        itemRemoved: (state, {payload}) => {
            const { typeId, id } = payload;
            const itemsByType = state.itemsInCart;
            if (!itemsByType.byId || !itemsByType.byId[typeId] || itemsByType.byId[typeId][id]) {
                return;
            }
            // Remove the deleted item ID.
            itemsByType.byId[typeId] = itemsByType.byId[typeId].filter(cartItemId => cartItemId !== id);
            if (itemsByType.byId[typeId].length === 0) {
                delete itemsByType.byId[typeId];
                itemsByType.allIds = itemsByType.allIds.filter(listTypeId => listTypeId !== typeId);
            }
            state.activeNotification = NOTIFICATION_TYPE.ItemsRemoved;
        },
        notificationDismissed: (state) => {
            state.activeNotification = null;
        },
        addItemsTransferred(state, {payload}) {
            state.transferredItems = payload;
        },
        transferredItemsCleared(state, {payload: shouldClearFromCart}) {
            const transferredItems = state.transferredItems;
            const itemsInCart = state.itemsInCart.byId;
            if (shouldClearFromCart) {
                // First, clear out transferred items from cart
                Object.keys(transferredItems).forEach(typeId => {
                    const transferredSet = new Set(transferredItems[typeId]);
                    itemsInCart[typeId] = itemsInCart[typeId].filter(itemId =>
                        !transferredSet.has(itemId)
                    );
                });
            }
            state.transferredItems = {};
        }
    }
});

export const {
    itemsIsLoading,
    cartLoaded,
    objectsValidating,
    objectsValidated,
    itemsLoadFailed,
    notificationDismissed,
    addItemsTransferred
} = cartSlice.actions;



export const removeAllItems = () => {
    return (dispatch, getState) => {
        dispatch(cartSlice.actions.allItemsRemoved());
        const itemsByType = getState().cart.itemsInCart;
        return localStorageUtils.setItem("itemIdsByType", itemsByType);
    };
};

export const addItems = (itemList) => {
    return (dispatch, getState) => {
        dispatch(cartSlice.actions.itemsAdded(itemList));
        const itemsByType = getState().cart.itemsInCart;
        return localStorageUtils.setItem("itemIdsByType", itemsByType);
    };
};

export const removeItem = (typeId, id) => {
    return (dispatch, getState) => {
        dispatch(cartSlice.actions.itemRemoved({typeId, id}));
        const itemsByType = getState().cart.itemsInCart;
        return localStorageUtils.setItem("itemIdsByType", itemsByType);
    };
};

export function clearTransferredItems(shouldClearFromCart) {
    return (dispatch, getState) => {
        dispatch(cartSlice.actions.transferredItemsCleared(shouldClearFromCart));
        const itemsByType = getState().cart.itemsInCart;
        return localStorageUtils.setItem("itemIdsByType", itemsByType);
    };
}

/**
 * Gets items in cart for type.
 * @param {*} slice Redux slice for cart state
 * @param {string} typeId id of the type (e.g. experiment, dataset, etc.)
 * @returns A list of items currently in cart, returns an empty list if none.
 */
export function getItemsByType(slice, typeId) {
    return slice.itemsInCart.byId[typeId] || [];
}

export default cartSlice.reducer;

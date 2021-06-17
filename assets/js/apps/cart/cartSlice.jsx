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
            const { typeId } = payload;
            const id = String(payload.id);
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
        }
    }
});

export const {
    itemsIsLoading,
    cartLoaded,
    objectsValidating,
    objectsValidated,
    itemsLoadFailed,
    notificationDismissed
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

/**
 * Gets items in cart for category.
 * @param {*} slice Redux slice for cart state
 * @param {string} typeId Type id of the category (e.g. experiment, dataset, etc.)
 * @returns A list of items currently in cart, returns an empty list if none.
 */
export function getItemsByCategory(slice, typeId) {
    return slice.itemsInCart.byId[typeId] || [];
}

export default cartSlice.reducer;
import { action } from "@storybook/addon-actions";

/**
 * Create a mock redux store for Storybook stories.
 * @param {object} state Mock state
 * @returns A mock Redux store
 */
const makeMockStore = (state = {}) => {
    return {
        getState: () => {
            return state;
        },
        subscribe: () => 0,
        dispatch: action("dispatch"),
    };
};

export default makeMockStore;
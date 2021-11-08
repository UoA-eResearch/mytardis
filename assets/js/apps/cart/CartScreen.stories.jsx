import React from "react";
import makeMockStore from "@apps/shared/makeMockStore";
import { CartScreen } from "./index";
import { Provider } from "react-redux";

const store = makeMockStore({
    cart: {
        itemsInCart: {
            allIds: [
                "experiment"
            ],
            byId: {
                experiment: [
                    "61"
                ]
            }
        },
        status: "INITIAL",
        activeNotification: null
    },

});
export default {
    component: CartScreen,
    title: "Cart/Cart screen",
    decorators: [story => <div style={{ padding: "3rem" }}>
        <Provider store={store}>{story()}</Provider>
    </div>],
    parameters: { actions: { argTypesRegex: "^on.*" } }
};

const Template = (args) => <CartScreen {...args} />;

export const Default = Template.bind({});
Default.args = {};
import TYPE_ATTRIBUTES from "../typeAttributes.json";
import React from 'react'
import TypeAttributesList from "./TypeAttributesList";
import { Provider } from "react-redux";
import makeMockStore from "../../../util/makeMockStore";


export default {
    component: TypeAttributesList,
    title: 'Filters/Type attributes list',
    decorators: [story =>
        
            <div style={{ padding: '3rem', width: '400px' }}>{story()}</div>
        ],
    excludeStories: /.*Data$/,
};

const typeAttributesData = {
    types: TYPE_ATTRIBUTES
}

export const Default = () => {
    const mockStore = makeMockStore({filters:typeAttributesData});
    return (
        <Provider store={mockStore}>
            <TypeAttributesList typeId="projects" />
        </Provider>
    );
};
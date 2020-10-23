import React from "react";
import Pager from "./Pager";
import makeMockStore from "../util/makeMockStore";
import { Provider } from "react-redux";

export default {
    component: Pager,
    title: "Pager",
    decorators: [story => <Provider store={store}><div style={{ padding: "3rem" }}>{story()}</div></Provider>],
    excludeStories: /.*Data$/
};

export const paginationData = {
    pageNumber: {
        projects: 1,
        experiments: 1,
        datasets: 1,
        datafiles: 1
    },
    pageSize: {
        projects: 50,
        experiments: 50,
        datasets: 50,
        datafiles: 50
    }
};

const store = makeMockStore(paginationData);

export const Default = () => (
    <Pager objectType="experiments" />
);
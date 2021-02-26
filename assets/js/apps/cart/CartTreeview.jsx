import React, { useState } from "react";
import { Treebeard } from "react-treebeard";
import { flatten } from "underscore";

const exampleData = [{
    name: "siNET",
    toggled: true,
    children: [
        {
            name: "parent",
            children: [
                { name: "child1" },
                { name: "child2" }
            ]
        },
        {
            name: "loading parent",
            loading: true,
            children: []
        },
        {
            name: "parent",
            children: [
                {
                    name: "nested parent",
                    children: [
                        { name: "nested child 1" },
                        { name: "nested child 2" }
                    ]
                }
            ]
        }
    ]
},
{
    name: "Gastroblastoma",
    toggled: false,
    children: [
        {
            name: "parent",
            children: [
                { name: "child1" },
                { name: "child2" }
            ]
        },
        {
            name: "loading parent",
            loading: true,
            children: []
        },
        {
            name: "parent",
            children: [
                {
                    name: "nested parent",
                    children: [
                        { name: "nested child 1" },
                        { name: "nested child 2" }
                    ]
                }
            ]
        }
    ]
}
];

const CartTreeview = () => {
    const [data, setData] = useState(exampleData);
    const [cursor, setCursor] = useState(false);

    const onToggle = (node, toggled) => {
        if (cursor) {
            cursor.active = false;
        }
        node.active = true;
        if (node.children) {
            node.toggled = toggled;
        }
        setCursor(node);
        // setData(Object.assign({}, data))
        // this.setState(() => ({cursor: node, data: data}));
        setData(data);
    };

    return (
        <Treebeard data={data} onToggle={onToggle}
            decorators={
                {
                    Container: (props) => {
                        return (
                            <div onClick={props.onClick}>
                                    // Hide Toggle When Terminal Here
                                <props.decorators.Toggle />
                                <props.decorators.Header />
                            </div>
                        );
                    }
                }}
            style={{
                tree: {
                    base: {
                        margin: "1rem 0",
                        padding: "1rem",
                        height: "500px",
                        // backgroundColor: "white",
                        // color: "black",
                        // boxShadow: "0 0.125rem 0.25rem rgba(0, 0, 0, 0.075) !important"
                    },
                    // node: {
                    //     activeLink: {
                    //         backgroundColor: "#5dabff"
                    //     }
                    // }
                }
            }} />
    );
};

export default CartTreeview;
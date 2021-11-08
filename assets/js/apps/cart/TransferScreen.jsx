import React, { useEffect, useState } from "react";
import { useCreateTransferMutation, useGetObjectByIdQuery, useGetRemoteHostsQuery, useGetSiteQuery, useValidateTransferQuery } from "../shared/api";
import PropTypes from "prop-types";
import { Button, Form, Modal } from "react-bootstrap";
import { Link, Redirect, Route, Switch, useHistory, useParams, useRouteMatch } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { addItemsTransferred, clearTransferredItems } from "./cartSlice";
import { BsChevronLeft, BsExclamationTriangle, BsExclamationTriangleFill } from "react-icons/bs";
import { FiExternalLink } from "react-icons/fi";
import { TypeTabs } from "../shared/TypeTabs";
import { QueryStatus } from "@reduxjs/toolkit/dist/query";
import { Alert } from "react-bootstrap";
import humanFileSize from "../shared/humanFileSize";

// eslint-disable-next-line complexity
function CartItemRow({ typeId, id, canTransfer }) {
    const { data: site, isLoading: isSiteLoading } = useGetSiteQuery();
    const endpointName = site ? site.types[typeId].endpoint_name : null;
    const { isLoading: isObjectLoading, data: item } = useGetObjectByIdQuery({
        name: endpointName,
        id
    }, {
        // Wait for site query to finish loading.
        skip: isSiteLoading
    });
    if (isSiteLoading || isObjectLoading) {
        return <tr></tr>;
    }

    if (!item) {
        return <tr>
            <td>
                Error loading item.
            </td>
        </tr>;
    }
    const nameField = site.types[typeId].name_field;
    const url = site.types[typeId].details_uri + id;
    const name = item[nameField];
    return (<tr className={canTransfer ? null : "cart-item--invalid"}>
        <td className="type-item-list--remove">
            {canTransfer ? null : <BsExclamationTriangleFill title="This item can't be transferred because it belongs to a project or dataset that is not associated with the chosen transfer destination." />}
        </td>
        <td className="type-item-list--name">
            {/* Name cell */}
            <a href={url} target="_blank" rel="noopener noreferrer">{name} <FiExternalLink /></a> 
        </td>
        <td className="type-item-list--size">
            <span>{humanFileSize(item.size)}</span>
        </td>
    </tr>);
}

CartItemRow.propTypes = {
    typeId: PropTypes.string.isRequired,
    id: PropTypes.string.isRequired,
    canTransfer: PropTypes.bool
};



export function CartTypeTabs({selectedRemoteHost, selectedType, onChange}) {
    const {data: site} = useGetSiteQuery({});
    const counts = useSelector(state => {
        if (!site) {
            return null;
        }
        const types = site.types;
        const typeKeys = Object.keys(types);
        return typeKeys.map(key => {
            const typeItemsInCart = state.cart.itemsInCart.byId[key] || [];
            return {
                name: site.types[key].collection_name,
                id: key,
                hitTotal: typeItemsInCart.length
            };
        });
    });
    if (!counts) {
        return null;
    } else {
        return (<TypeTabs counts={counts} selectedType={selectedType} onChange={onChange} />);
    }
}

/**
 * Create a React hook for storing the currently selected type. 
 * Get query API, in order to provide an initially-selected type.
 * @returns A state variable for a type key, and a callback for changing it.
 */
function useSelectedTypeState() {
    const [ selectedType, setSelectedType ] = useState();
    const {data: site, isLoading } = useGetSiteQuery({});

    useEffect(() => {
        // Set default type when our list of types is loaded.
        // Make sure it's only done when types loaded.
        if (site) {
            setSelectedType(Object.keys(site.types)[0]);
        }
    }, [setSelectedType, site]);
    return [ selectedType, setSelectedType ];
}

function useGetHostInfoQuery(hostId) {
    return useGetRemoteHostsQuery(null, {
        selectFromResult: res => {
            if (res.status !== "fulfilled") {
                return res;
            }
            const data = res.data;
            const hostsById = Object.fromEntries(
                data.map(host => [host.id, host])
            );
            return Object.assign({}, res, {
                data: hostsById[hostId]
            });
        }
    });
}

function InvalidItemsWarning({ hostId }) {
    const [open, setOpen] = useState(false);
    const {data: hostInfo, isLoading } = useGetHostInfoQuery(hostId);
    const {data: invalidCount, isLoading: isValidationLoading } = useInvalidTransferItemsCount({remoteHostId: hostId});
    if (isLoading || isValidationLoading) {
        return <div className="my-3">
            <div className="spinner-border" role="status">
                <span className="sr-only">Loading...</span>
            </div>
        </div>;
    }
    if (invalidCount === 0 || !hostInfo) {
        return null;
    } 
    const remoteHostName = hostInfo.name;
    return <Alert variant="warning" className="mt-3">
        <BsExclamationTriangle className="mr-1" /> Some cart items can't be transferred to {remoteHostName}.
    </Alert>;
}

// eslint-disable-next-line complexity
function RemoteHostDropdown({selectedId, onSelect}) {
    const { data: remoteHosts, isLoading, error } = useGetRemoteHostsQuery();
    let output = null;
    if (isLoading) {
        output = <>
            <select className="form-control"
                aria-label="Transfer destination"
                size="lg"
                id="transfer-page--dropdown"
                disabled
            >
                <option key="notselected">Loading...</option>
            </select>
        </>;
    }
    else if (error) {
        output = <p>Error occurred while fetching list of Globus endpoints.</p>;
    } else {
        const remoteHostIds = remoteHosts.map(host => host.id);
        const hostsById = Object.fromEntries(
            remoteHosts.map(host => [host.id, host])
        );
        const selected = selectedId ? hostsById[selectedId].name : "";
        let remoteHostOptions;
        if (!remoteHosts || remoteHosts.length === 0) {
            remoteHostOptions = <option>No destinations available.</option>;
        } else {
            remoteHostOptions = remoteHosts.map(host => 
                <option key={host.id}>
                    {host.name}
                </option>);
            // Add a default, unselected option.
            remoteHostOptions.unshift(<option key="notselected">Select a destination</option>);
        }
        const handleSelected = (e) => {
            e.preventDefault();
            const selectedIndex = e.target.selectedIndex;
            if (selectedIndex === 0) {
                onSelect(null);
            } else {
                onSelect(remoteHostIds ? parseInt(remoteHostIds[selectedIndex - 1]) : null);
            }
        };
        output = <select className="form-control"
            aria-label="Transfer destination"
            size="lg"
            value={selected}
            id="transfer-page--dropdown"
            onChange={handleSelected}
        >
            {remoteHostOptions}
        </select>;
    }
    return <div className="transfer-screen--remotehost-list">
        {output}
    </div>;
}

RemoteHostDropdown.propTypes = {
    selectedId: PropTypes.string,
    onSelect: PropTypes.func.isRequired
};

function TypeItemList({ children }) {
    return (<>
    <table className="table">
        <thead>
            <tr>
                <th></th>
                <th>Name</th>
                <th>Size</th>
            </tr>
        </thead>
        <tbody>
            {children}
        </tbody>
    </table>
    {children.length === 0 && 
        <div className="mt-5 d-flex justify-content-center" role="status">
            No items to be transferred.
        </div>
    }</>);
}

TypeItemList.propTypes = {
    children: PropTypes.oneOfType([
        PropTypes.arrayOf(PropTypes.node),
        PropTypes.node
    ]).isRequired
};

const VALID_TRANSFER_FILTER_STATES = {
    All: "ALL",
    Invalid: "INVALID",
    Valid: "VALID"
};


function getItemsByState(items = [], invalidItems = [], validState) {
    // const invalidTypeItems = validationErrors.invalidItems ? validationErrors.invalidItems[type] : [];
    // const typeItems = items.byId[typeId];
    switch (validState) {
        case VALID_TRANSFER_FILTER_STATES.All:
            return items;
        case VALID_TRANSFER_FILTER_STATES.Invalid:
            return invalidItems;
        case VALID_TRANSFER_FILTER_STATES.Valid: {
            const invalidSet = new Set(invalidItems);
            return items.filter(item => !invalidSet.has(item));
        }
    }
}

function getInvalidItemsCount(invalidItems) {
    if (!invalidItems) {
        return 0;
    }
    return Object.keys(invalidItems).reduce(
        (acc, typeId) => invalidItems[typeId].length + acc, 0);

}


// eslint-disable-next-line complexity
export function TransferrableItemList({selectedRemoteHost}) {
    const {data: site, isLoading, error } = useGetSiteQuery({});
    const [ selectedType, setSelectedType ] = useSelectedTypeState();
    const cartItems = useSelector(state => state.cart.itemsInCart.byId);
    const hasSelectedRemoteHost = selectedRemoteHost !== undefined && selectedRemoteHost !== null;
    const { data: validationErrors,
        error: validationQueryError
    } = useValidateTransferQuery({
        remoteHostId: selectedRemoteHost,
        items: cartItems
    }, {
        skip: !hasSelectedRemoteHost,
        selectFromResult: (res) => {
            if (res.isSuccess) {
                const data = res.data;
                if (hasSelectedRemoteHost && 
                    data &&
                    data.invalid_items) {
                    // Return the inner invalid_items object.
                    return Object.assign({}, res, {
                        data: data.invalid_items
                    });
                } else {
                    return Object.assign({}, res, {
                        data: {}
                    });
                }
            }
            // Return an empty object if not yet loaded.
            return Object.assign({}, res, {
                data: {}
            });
        }
    });
    const items = useSelector(state => state.cart.itemsInCart || {});
    if (isLoading) {
        return <div className="spinner-border" role="status">
            <span className="sr-only">Loading...</span>
        </div>;
    }
    if (error) {
        return <p>Error loading items.</p>;
    }
    if (hasSelectedRemoteHost && validationQueryError) {
        console.log(validationQueryError.message);
        return <p>Error loading items.</p>;
    }
    const types = Object.keys(site.types);

    const tabItems = types.map(typeId => {
        const typeItems = items.byId[typeId];
        const hitTotal = typeItems ? typeItems.length : 0;
        // If there are validation errors for this type, display
        // a warning in the tab.
        const hasWarning = validationErrors[typeId] && validationErrors[typeId].length > 0;
        return {
            name: site.types[typeId].collection_name,
            id: typeId,
            hitTotal: hitTotal,
            hasWarning
        };
    }
    );
    return <>
        <TypeTabs counts={tabItems} selectedType={selectedType} onChange={setSelectedType} />
        {types.map(typeId => {
            const invalidItemSet = new Set(validationErrors[typeId]);
            const typeItems = items.byId[typeId] || [];
            return <div className={selectedType !== typeId ? "d-none type-item-list" : "type-item-list"} key={typeId}>
                <TypeItemList>
                    {typeItems.map(item => (
                        <CartItemRow typeId={typeId} id={item} canTransfer={!invalidItemSet.has(item)} key={typeId + ":" + item} />
                    ))}
                </TypeItemList>
            </div>;
        })}
    </>;
}
const TRANSFER_STATE = {
    Initial: "Initial",
    TransferRequested: "TransferRequested", // set to start a transfer
    NeedConfirmation: "NeedConfirmation", // has invalid items
    Confirmed: "Confirmed", // confirmed
    Transferring: "Transferring", // transferring
    Transferred: "Transferred" // transferred
};

function useInvalidTransferItemsCount({remoteHostId}) {
    const cartItems = useSelector(state => state.cart.itemsInCart.byId);
    return useValidateTransferQuery({
        remoteHostId,
        items: cartItems
    }, {skip: remoteHostId === undefined, selectFromResult: (res) => {
        if (res.status === "fulfilled") {
            const data = res.data;
            let count = 0;
            if (data) {
                count = getInvalidItemsCount(data.invalid_items);
            }
            // Replace the list of invalid items with the count.
            return Object.assign({}, res, {data: count});
        }
        return res;
    }});
}

function getValidItems(cartItems, invalidItems) {
    const validItems = {};
    Object.keys(cartItems).forEach(
        typeId => {
            const invalidSet = new Set(invalidItems[typeId]);
            validItems[typeId] = cartItems[typeId].filter(item => !invalidSet.has(item));
        }
    );
    return validItems;
}

function ConfirmTransferDialog({numInvalidItems, onConfirm, onCancel}) {
    return (
        <Modal show={true} onHide={onCancel}>
            <Modal.Header closeButton>
                <Modal.Title>Do you want to proceed with this transfer?</Modal.Title>
            </Modal.Header>
            <Modal.Body>{numInvalidItems} {numInvalidItems === 1 ? "item" : "items" } will not be included in the transfer because of restrictions on locations where these items can be transferred.</Modal.Body>
            <Modal.Footer>
                <Button variant="secondary" onClick={onCancel}>
                        Cancel
                </Button>
                <Button variant="primary" onClick={onConfirm}>
                        Yes, proceed
                </Button>
            </Modal.Footer>
        </Modal>
    );
}

ConfirmTransferDialog.propTypes = {
    numInvalidItems: PropTypes.number.isRequired,
    onConfirm: PropTypes.func.isRequired,
    onCancel: PropTypes.func.isRequired
};

// eslint-disable-next-line complexity
function CreateTransferDialog({remoteHostId, transferState, setTransferState}) {
    const cartItems = useSelector(state => state.cart.itemsInCart.byId);
    const [triggerTransfer, {status: transferMutationStatus}] = useCreateTransferMutation();
    const {data: invalidItems, isLoading: isValidationLoading, error: validationError } = useValidateTransferQuery({
        remoteHostId,
        items: cartItems
    });
    const numInvalidItems = invalidItems ? getInvalidItemsCount(invalidItems.invalid_items) : 0;
    let validItems = {};
    if (invalidItems) {
        validItems = getValidItems(cartItems, invalidItems.invalid_items);
    } 
    const dispatch = useDispatch();
    // const {data: numInvalidItems, isLoading: isValidationLoading} = useInvalidTransferItemsCount({remoteHostId});
    useEffect(() => {
        if (transferState !== TRANSFER_STATE.TransferRequested || isValidationLoading || validationError) {
            // If validation is still being loaded, wait until it's
            // loaded.
            return;
        }
        
        if (!numInvalidItems) {
            setTransferState(TRANSFER_STATE.Confirmed);
        } else {
            setTransferState(TRANSFER_STATE.NeedConfirmation);
        }

    }, [transferState, invalidItems, numInvalidItems, validationError, isValidationLoading]);

    useEffect(() => {
        if (transferState === TRANSFER_STATE.Confirmed) {
            triggerTransfer({remoteHostId, items: validItems});
            setTransferState(TRANSFER_STATE.Transferring);
        }
    }, [transferState]);
    useEffect(() => {
        if (transferMutationStatus === QueryStatus.fulfilled) {
            setTransferState(TRANSFER_STATE.Transferred);
        }
    }, [transferMutationStatus]);
    if (transferState === TRANSFER_STATE.NeedConfirmation) {
        return (
            <ConfirmTransferDialog numInvalidItems={numInvalidItems}
                onConfirm={() => setTransferState(TRANSFER_STATE.Confirmed)}
                onCancel={() => setTransferState(TRANSFER_STATE.Initial)}
            />
        );
    }
    if (transferState === TRANSFER_STATE.Confirmed) {
        return <p>Sending...</p>;
    }
    if (transferState === TRANSFER_STATE.Transferred) {
        dispatch(addItemsTransferred(validItems));
        return <Redirect to="/transfer/done" />;
    }
    else { 
        return null;
    }
}

function TransferScreen(props) {
    const [selectedRemoteHost, setSelectedRemoteHost] = useState();
    const history = useHistory();
    const goToConfirmScreen = () => {
        history.push(`/transfer/${selectedRemoteHost}`);
    };
    return <div>
        <div className="mb-3">
            <Link to="/"><BsChevronLeft />Go back</Link>
        </div>
        <h1 className="mb-2 h4 text-secondary font-weight-light">Transfer to a Globus endpoint</h1>
        <h2 className="mb-3 h1">Select a transfer destination</h2>
        <p className="text-secondary">Can't see your Globus endpoint? Contact your data repository support team to add it to MyTardis.</p>
        <RemoteHostDropdown selectedId={selectedRemoteHost} onSelect={setSelectedRemoteHost} />
        <div className="d-flex justify-content-between mt-5">
            <button 
                className="btn btn-primary"
                disabled={!selectedRemoteHost}
                aria-disabled={!selectedRemoteHost}
                onClick={goToConfirmScreen}
            >
                Continue
            </button>
        </div>

    </div>;
}

// function Transfer

function TransferConfirmScreen() {
    const { hostId } = useParams();
    const [transferState, setTransfer] = useState(TRANSFER_STATE.Initial);
    const { data: hostInfo, isLoading: isLoadingHostInfo } = useGetHostInfoQuery(hostId);
    const {data: invalidCount, isLoading: isValidationLoading} = useInvalidTransferItemsCount({remoteHostId: hostId});
    return (<>
        <div className="mb-3">
            <Link to="/transfer"><BsChevronLeft />Go back</Link>
        </div>
        <h1 className="mb-2 h4 text-secondary font-weight-light">Transfer to a Globus endpoint</h1>
        <h2 className="mb-3 h1">Review items to be transferred</h2>
        <p className="text-secondary">To change, go back to the cart to add or remove items.</p>
        <section className="my-4">
            <dl className="d-flex border-bottom">
                <dt className="col-md-8">
                    Transfer destination
                </dt>
                <dd className="col-md-2">
                    {hostInfo ? hostInfo.name : null}
                </dd>
                <dd className="col-md-2 text-right">
                    <Link to="/transfer">Change</Link>
                </dd>
            </dl>
        </section>
        <InvalidItemsWarning hostId={hostId} />
        <TransferrableItemList selectedRemoteHost={hostId} />
        <div className="mt-4">
            <button 
                className="btn btn-primary"
                onClick={() => setTransfer(TRANSFER_STATE.TransferRequested)}
            >
                Start transfer
            </button>
        </div>
        <CreateTransferDialog 
            remoteHostId={hostId} 
            transferState={transferState} 
            setTransferState={setTransfer} 
        />
    </>);
}

function TransferCompletedScreen() {
    const dispatch = useDispatch();
    const history = useHistory();
    const transferredItems = useSelector(state => state.cart.transferredItems);
    const [shouldRemoveTransferred, setShouldRemoveTransferred] = useState(true);
    const numTransferred = Object.keys(transferredItems).reduce(
        (acc, typeId) => acc + transferredItems[typeId].length, 0);
    const toggleShouldRemoveTransferred = () => {
        setShouldRemoveTransferred(!shouldRemoveTransferred);
    };
    const handleVisitCart = () => {
        dispatch(clearTransferredItems(shouldRemoveTransferred));
        history.replace("/");
    };

    if (numTransferred === 0) {
        // If there aren't any transferred items, go back to the cart.
        const redirectPath = "/";
        return <Redirect to={redirectPath} />;
    }
    
    return <>
        <h1 className="mb-2 h4 text-secondary font-weight-light">Transfer to a Globus endpoint</h1>
        <h2 className="h1 mb-3">Transfer started</h2>
        <p><strong>{numTransferred} {numTransferred === 1 ? "item" : "items"} have started transferring.</strong></p>
        <p>Depending on the size of the items it may take several hours for the items to finish transferring to the destination. You can check progress of the transfer through the Transfers page (todo).</p>
        <Form.Check 
            type="checkbox" 
            checked={shouldRemoveTransferred}
            onChange={toggleShouldRemoveTransferred}
            id="shouldTransfer"
            label="Remove transferred items from cart" 
        />
        <div className="d-flex justify-content-between mt-4">
            <Button role="link" onClick={handleVisitCart} className="btn btn-primary" to="/cart">Go back to cart</Button>
        </div>
    </>;
}

function TransferRoute(props) {
    const match = useRouteMatch();
    return <Switch>
        <Route path={`${match.path}/done`}>
            <TransferCompletedScreen />
        </Route>
        <Route path={`${match.path}/:hostId`}>
            <TransferConfirmScreen />
        </Route>
        <Route path={`${match.path}`}>
            <TransferScreen />
        </Route>
    </Switch>;
}

export default TransferRoute;
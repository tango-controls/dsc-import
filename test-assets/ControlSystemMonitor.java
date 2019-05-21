package fr.soleil.tango.server.cs.monitor;

import java.sql.Date;
import java.text.SimpleDateFormat;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

import org.apache.commons.lang3.ArrayUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.tango.DeviceState;
import org.tango.server.ServerManager;
import org.tango.server.annotation.Attribute;
import org.tango.server.annotation.Command;
import org.tango.server.annotation.Delete;
import org.tango.server.annotation.Device;
import org.tango.server.annotation.DynamicManagement;
import org.tango.server.annotation.Init;
import org.tango.server.annotation.State;
import org.tango.server.annotation.StateMachine;
import org.tango.server.annotation.Status;
import org.tango.server.annotation.TransactionType;
import org.tango.server.attribute.log.LogAttribute;
import org.tango.server.dynamic.DynamicManager;
import org.tango.utils.DevFailedUtils;

import fr.esrf.Tango.DevFailed;
import fr.esrf.Tango.DispLevel;
import fr.esrf.TangoApi.ApiUtil;
import fr.esrf.TangoApi.Database;
import fr.esrf.TangoApi.DeviceData;
import fr.esrf.TangoApi.DeviceProxy;
import fr.esrf.TangoApi.Group.Group;
import fr.esrf.TangoApi.Group.GroupAttrReply;
import fr.esrf.TangoApi.Group.GroupAttrReplyList;

/**
 * Utility device to monitor a Control System. <br>
 * <br>
 * Can do many things: <br>
 * - get status or states of group of devices<br>
 * - kill/start group of devices<br>
 * - execute group command<br>
 * <br>
 * Each command is available :<br>
 * - either with a device name pattern like ans&#042;/ae/alim&#042;<br>
 * - or by device class name like StateComposer<br>
 * <br>
 */
@Device(transactionType = TransactionType.DEVICE)
public final class ControlSystemMonitor {

    private static final SimpleDateFormat DATE_FORMAT = new SimpleDateFormat("dd-MM-yyyy HH:mm:ss");
    private static final String WAITING_FOR_REQUEST = "Waiting for request";
    private static final int DEFAULT_TIMEOUT = 3000;
    private static final String DESC_1 = "The device pattern (wildcard char is *), timeout (optional)";
    private static final String DESC_2 = "The device class pattern (wildcard char is *), timeout (optional)";
    private final Logger logger = LoggerFactory.getLogger(ControlSystemMonitor.class);
    @Status
    private volatile String status;
    @State
    private volatile DeviceState state;

    @DynamicManagement
    DynamicManager dynamicManager;

    @Attribute
    private volatile String[] lastResult = new String[0];

    private Database tangoDB;
    private Group starterGroup;
    private ControlSystemHelper controlSystemHelper;

    public static void main(final String[] args) {
        ServerManager.getInstance().start(args, ControlSystemMonitor.class);
    }

    @Init(lazyLoading = true)
    @StateMachine(endState = DeviceState.ON)
    public void init() throws DevFailed {
        lastResult = new String[0];
        dynamicManager.addAttribute(new LogAttribute(1000, logger));
        tangoDB = ApiUtil.get_db_obj();
        controlSystemHelper = new ControlSystemHelper(tangoDB);
        final String[] servers = tangoDB.get_server_list();
        final String[] classes = tangoDB.get_class_list("*");
        logger.debug("connection to tango db OK. contains {} servers and {} classes", servers.length, classes.length);
        String[] starters;
        try {
            starters = controlSystemHelper.getExportedDevicesForClass("Starter");
        } catch (final DevFailed e) {
            // there is no starters on this CS
            starters = new String[] {};
        }
        starterGroup = controlSystemHelper.createGroup(starters, DEFAULT_TIMEOUT);
        logger.debug("starter group created with size of {} ", starters.length);
        status = "Control system contains " + servers.length + " servers and " + classes.length + " classes\n";
        status = status + "controling " + starters.length + " starters";
    }

    @Delete
    public void delete() throws DevFailed {
        dynamicManager.clearAll();
    }

    /**
     * Execute Init command on a group of devices
     *
     * @param in
     *            The device class pattern (wildcard char is *) ,
     *            timeout(optional)
     * @throws DevFailed
     */
    @Command(inTypeDesc = "The device class pattern (wildcard char is *) on which Init command will be executed, timeout(optional)", displayLevel = DispLevel._EXPERT)
    @StateMachine(deniedStates = DeviceState.INIT)
    public void initClassForget(final String[] in) throws DevFailed {
        controlSystemHelper.initClass(true, in);
    }

    /**
     * Execute Init command on a group of devices
     *
     * @param className
     *            The device class pattern (wildcard char is *)
     */
    @Command(inTypeDesc = "The device class pattern (wildcard char is *) on which Init command will be executed")
    @StateMachine(deniedStates = { DeviceState.INIT, DeviceState.RUNNING })
    public void initClass(final String className) {
        // detach execution and log result in an attribute
        new Thread(new Runnable() {

            @Override
            public void run() {
                try {
                    state = DeviceState.RUNNING;
                    status = "Sending Init command to " + className + " in progress";
                    lastResult = ArrayUtils.add(controlSystemHelper.initClass(false, className), 0, getExecutionDate());
                } catch (final DevFailed e) {
                    lastResult = new String[] { getExecutionDate(), DevFailedUtils.toString(e) };
                    logger.error("Failed to init {}", DevFailedUtils.toString(e));
                } finally {
                    state = DeviceState.ON;
                    status = WAITING_FOR_REQUEST;
                }
            }
        }).start();
    }

    /**
     * Execute Init command on a group of devices
     *
     * @param className
     *            The device class pattern (wildcard char is *)
     */
    @Command(inTypeDesc = "The device class pattern (wildcard char is *) on which Init command will be executed")
    @StateMachine(deniedStates = { DeviceState.INIT, DeviceState.RUNNING })
    public void initFaultyClass(final String className) {
        // detach execution and log result in an attribute
        new Thread(new Runnable() {

            @Override
            public void run() {
                try {
                    state = DeviceState.RUNNING;
                    status = "Sending Init command to " + className + " in progress";
                    lastResult = ArrayUtils.add(controlSystemHelper.initFaultyClass(false, className), 0,
                            getExecutionDate());
                } catch (final DevFailed e) {
                    lastResult = new String[] { getExecutionDate(), DevFailedUtils.toString(e) };
                    logger.error("Failed to init {}", DevFailedUtils.toString(e));
                } finally {
                    state = DeviceState.ON;
                    status = WAITING_FOR_REQUEST;
                }
            }
        }).start();
    }

    /**
     * Execute a command on a group of devices
     *
     * @param in
     *            The device class pattern (wildcard char is *) ,command name,
     *            timeout(optional)
     * @throws DevFailed
     */
    @Command(inTypeDesc = "The device class pattern (wildcard char is *) on which command will be executed,command name, timeout(optional)", displayLevel = DispLevel._EXPERT)
    @StateMachine(deniedStates = DeviceState.INIT)
    public void commandClass(final String[] in) throws DevFailed {
        final String className = in[0];
        final String commandName = in[1];
        final int timeout = controlSystemHelper.getTimeout(in);

        final String[] devices = controlSystemHelper.getExportedDevicesForClass(className);
        logger.debug("command {} on devices {}", commandName, Arrays.toString(devices));
        controlSystemHelper.groupedCommandForget(timeout, commandName, devices);
    }

    private String getExecutionDate() {
        final StringBuilder sb = new StringBuilder("execution date is ");
        final String now = DATE_FORMAT.format(new Date(System.currentTimeMillis()));
        sb.append(now).append("\n");
        return sb.toString();
    }

    /**
     * Get an attribute value for devices of a class and report result in lastStateResult
     * attribute
     *
     * @param className
     *            The device class pattern (wildcard char is *)
     * @param attributeName the attribute to reas
     * @return
     * @throws DevFailed
     */
    @Command(inTypeDesc = "The class name and attribute name", outTypeDesc = "The attribute value of all class devices")
    @StateMachine(deniedStates = { DeviceState.INIT, DeviceState.RUNNING })
    public void getClassAttributes(final String[] in) throws DevFailed {
        final String className = in[0];
        final String attributeName = in[1];
        // detach execution and log result in an attribute
        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    state = DeviceState.RUNNING;
                    status = "Retrieving attribute " + attributeName + " of " + className;
                    lastResult = ArrayUtils.add(controlSystemHelper.getClassAttribute(attributeName, in), 0,
                            getExecutionDate());
                } catch (final DevFailed e) {
                    lastResult = new String[] { getExecutionDate(), DevFailedUtils.toString(e) };
                    logger.error("Failed to get state {}", DevFailedUtils.toString(e));
                } finally {
                    state = DeviceState.ON;
                    status = WAITING_FOR_REQUEST;
                }
            }
        }).start();
    }

    /**
     * Get state for devices of a class and report result in lastStateResult
     * attribute
     *
     * @param in
     *            The device class pattern (wildcard char is *), timeout
     *            (optional)
     * @return
     * @throws DevFailed
     */
    @Command(inTypeDesc = "The class name", outTypeDesc = "The state of all class devices")
    @StateMachine(deniedStates = { DeviceState.INIT, DeviceState.RUNNING })
    public void getClassState(final String className) throws DevFailed {
        // detach execution and log result in an attribute
        new Thread(new Runnable() {

            @Override
            public void run() {
                try {
                    state = DeviceState.RUNNING;
                    status = "Retrieving state of " + className;
                    lastResult = ArrayUtils.add(controlSystemHelper.getClassState(className), 0, getExecutionDate());
                } catch (final DevFailed e) {
                    lastResult = new String[] { getExecutionDate(), DevFailedUtils.toString(e) };
                    logger.error("Failed to get state {}", DevFailedUtils.toString(e));
                } finally {
                    state = DeviceState.ON;
                    status = WAITING_FOR_REQUEST;
                }
            }
        }).start();
    }

    /**
     * Get state of devices
     *
     * @param in
     *            The device pattern (wildcard char is *), timeout (optional)
     * @return
     * @throws DevFailed
     */
    @Command(inTypeDesc = DESC_1, outTypeDesc = "The state of all class devices", displayLevel = DispLevel._EXPERT)
    @StateMachine(deniedStates = DeviceState.INIT)
    public String[] getClassStateSync(final String[] in) throws DevFailed {
        return controlSystemHelper.getClassState(in);
    }

    /**
     * Get status of devices of a class
     *
     * @param in
     *            The device class pattern (wildcard char is *), timeout
     *            (optional)
     * @return
     * @throws DevFailed
     */
    @Command(inTypeDesc = DESC_2, outTypeDesc = "The status of all class devices")
    @StateMachine(deniedStates = { DeviceState.INIT, DeviceState.RUNNING })
    public void getClassStatus(final String className) throws DevFailed {
        // detach execution and log result in an attribute
        new Thread(new Runnable() {

            @Override
            public void run() {
                try {
                    state = DeviceState.RUNNING;
                    status = "Retrieving status of " + className;
                    lastResult = ArrayUtils.add(controlSystemHelper.getClassStatus(className), 0, getExecutionDate());
                } catch (final DevFailed e) {
                    lastResult = new String[] { getExecutionDate(), DevFailedUtils.toString(e) };
                    logger.error("Failed to get status {}", DevFailedUtils.toString(e));
                } finally {
                    state = DeviceState.ON;
                    status = WAITING_FOR_REQUEST;
                }
            }
        }).start();
    }

    /**
     * Get status of devices of a class
     *
     * @param in
     *            The device class pattern (wildcard char is *), timeout
     *            (optional)
     * @return
     * @throws DevFailed
     */
    @Command(inTypeDesc = DESC_2, outTypeDesc = "The status of all class devices", displayLevel = DispLevel._EXPERT)
    @StateMachine(deniedStates = DeviceState.INIT)
    public String[] getClassStatusSync(final String[] in) throws DevFailed {
        return controlSystemHelper.getClassStatus(in);
    }

    /**
     * Ping a group of devices
     *
     * @param in
     *            The device class pattern (wildcard char is *), timeout
     *            (optional)
     * @return
     * @throws DevFailed
     */
    @Command(inTypeDesc = DESC_2, outTypeDesc = "true if all devices are alive")
    @StateMachine(deniedStates = { DeviceState.INIT, DeviceState.RUNNING })
    public void pingClass(final String in) throws DevFailed {
        // detach execution and log result in an attribute
        new Thread(new Runnable() {

            @Override
            public void run() {
                try {
                    state = DeviceState.RUNNING;
                    status = "ping of " + in;
                    final String[] devices = controlSystemHelper.getExportedDevicesForClass(in);
                    logger.debug("ping {} devices {}", devices.length, Arrays.toString(devices));
                    final boolean hasPing = controlSystemHelper.createGroup(devices, 3000).ping(true);
                    lastResult = new String[] { getExecutionDate(), Boolean.toString(hasPing) };
                } catch (final DevFailed e) {
                    lastResult = new String[] { getExecutionDate(), DevFailedUtils.toString(e) };
                    logger.error("Failed to get status {}", DevFailedUtils.toString(e));
                } finally {
                    state = DeviceState.ON;
                    status = WAITING_FOR_REQUEST;
                }
            }
        }).start();
    }

    /**
     * Ping a group of devices
     *
     * @param in
     *            The device class pattern (wildcard char is *), timeout
     *            (optional)
     * @return
     * @throws DevFailed
     */
    @Command(inTypeDesc = DESC_2, outTypeDesc = "true if all devices are alive", displayLevel = DispLevel._EXPERT)
    @StateMachine(deniedStates = DeviceState.INIT)
    public boolean pingClassSynch(final String[] in) throws DevFailed {
        final String className = in[0];
        final int timeout = controlSystemHelper.getTimeout(in);
        final String[] devices = controlSystemHelper.getExportedDevicesForClass(className);
        logger.debug("ping {} devices {}", devices.length, Arrays.toString(devices));
        return controlSystemHelper.createGroup(devices, timeout).ping(true);
    }

    /**
     * Kill a group of servers
     *
     * @param in
     *            The device class pattern (wildcard char is *), timeout
     *            (optional)
     * @throws DevFailed
     */
    @Command(inTypeDesc = DESC_2, displayLevel = DispLevel._EXPERT)
    @StateMachine(deniedStates = DeviceState.INIT)
    public void killClass(final String[] in) throws DevFailed {
        final String className = in[0];
        final int timeout = controlSystemHelper.getTimeout(in);

        final String[] deviceNames = controlSystemHelper.getExportedDevicesForClass(className);
        killDeviceArray(deviceNames, timeout);
    }

    /**
     * Kill a group of servers
     *
     * @param in
     *            The device pattern (wildcard char is *), timeout (optional)
     * @throws DevFailed
     */
    @Command(inTypeDesc = DESC_1, displayLevel = DispLevel._EXPERT)
    @StateMachine(deniedStates = DeviceState.INIT)
    public void killDevices(final String[] in) throws DevFailed {
        final String devicePattern = in[0];
        int timeout = DEFAULT_TIMEOUT;
        if (in.length > 1) {
            timeout = Integer.parseInt(in[1]);
        }

        final String[] deviceNames = controlSystemHelper.getExportedDevices(devicePattern);
        killDeviceArray(deviceNames, timeout);
    }

    private void killDeviceArray(final String[] deviceNames, final int timeout) throws DevFailed {
        logger.debug("kill devices {}", Arrays.toString(deviceNames));
        // retrieve admin devices of the devices
        final Set<String> adminDevices = new HashSet<String>();
        for (final String deviceName : deviceNames) {
            try {
                adminDevices.add(new DeviceProxy(deviceName).adm_name());
            } catch (final DevFailed e) {
                logger.info("{} is not started, will not stop it", deviceName);
            }
        }
        logger.debug("will send kill to {}", adminDevices);
        if (adminDevices.size() > 0) {
            final Group group = controlSystemHelper.createGroup(adminDevices.toArray(new String[adminDevices.size()]),
                    timeout);
            group.command_inout_asynch("Kill", true, true);
            logger.debug("kill sent");
        }
    }

    /**
     * Start a group of Server throught devices of Starter class.
     *
     * @param in
     *            The device class pattern (wildcard char is *), timeout
     *            (optional)
     * @throws DevFailed
     */
    @Command(inTypeDesc = DESC_2, displayLevel = DispLevel._EXPERT)
    @StateMachine(deniedStates = DeviceState.INIT)
    public void startClass(final String[] in) throws DevFailed {
        final String className = in[0];
        int timeout = DEFAULT_TIMEOUT;
        if (in.length > 1) {
            timeout = Integer.parseInt(in[1]);
        }
        try {
            starterGroup.set_timeout_millis(timeout, true);
        } catch (final DevFailed e) {

        }
        // get all device of className
        final String[] deviceNames = tangoDB.get_device_name("*", className);
        startServers(deviceNames);
    }

    /**
     * Start a group of Server throught devices of Starter class.
     *
     * @param in
     *            The device pattern (wildcard char is *), timeout (optional)
     * @throws DevFailed
     */
    @Command(inTypeDesc = DESC_1, displayLevel = DispLevel._EXPERT)
    @StateMachine(deniedStates = DeviceState.INIT)
    public void startDevices(final String[] in) throws DevFailed {
        final String devicePattern = in[0];
        final int timeout = controlSystemHelper.getTimeout(in);
        try {
            starterGroup.set_timeout_millis(timeout, true);
        } catch (final DevFailed e) {

        }
        // retrieve servers of the devices
        final String[] deviceNames = controlSystemHelper.getDevices(devicePattern);
        startServers(deviceNames);
    }

    private synchronized void startServers(final String[] deviceNames) throws DevFailed {
        // retrieve servers of the devices
        final Set<String> serverToStart = new HashSet<String>();
        for (final String deviceName : deviceNames) {
            final String server = tangoDB.import_device(deviceName).server;
            serverToStart.add(server);
        }
        logger.debug("start servers {}", serverToStart);
        // find the starters that control this class
        final GroupAttrReplyList serverResults = starterGroup.read_attribute("Servers", true);
        for (final Object object : serverResults) {
            final GroupAttrReply reply = (GroupAttrReply) object;
            try {
                final String[] managedServers = reply.get_data().extractStringArray();
                for (final String server : serverToStart) {
                    if (Arrays.toString(managedServers).contains(server)) {
                        // starts the server on starter if it manages it
                        final DeviceData data = new DeviceData();
                        data.insert(server);
                        logger.debug("starting server {} on {}", server, reply.dev_name());
                        try {
                            starterGroup.get_device(reply.dev_name()).command_inout_asynch("DevStart", data);
                        } catch (final DevFailed e) {
                            logger.error("failed DevStart on starter {}: {}", reply.dev_name(),
                                    DevFailedUtils.toString(e));
                        }
                    }
                }
            } catch (final DevFailed e) {
                logger.error("failed reading attribute Servers on starter {}: {}", reply.dev_name(),
                        DevFailedUtils.toString(e));
            }
        }
    }

    /**
     * Execute Init command on a group of devices
     *
     * @param in
     *            The device pattern (wildcard char is *), timeout (optional)
     * @throws DevFailed
     */
    @Command(inTypeDesc = "The device pattern (wildcard char is *) on which command will be executed, timeout(optional)", displayLevel = DispLevel._EXPERT)
    @StateMachine(deniedStates = DeviceState.INIT)
    public void initDevicesForget(final String[] in) throws DevFailed {
        controlSystemHelper.initDevices(true, in);
    }

    /**
     * Execute Init command on a group of devices
     *
     * @param in
     *            The device pattern (wildcard char is *)
     */
    @Command(inTypeDesc = "The device pattern (wildcard char is *) on which command will be executed")
    @StateMachine(deniedStates = DeviceState.INIT)
    public void initDevices(final String in) {

        // detach execution and log result in an attribute
        new Thread(new Runnable() {

            @Override
            public void run() {
                try {
                    state = DeviceState.RUNNING;
                    status = "Sending Init command to " + in + " in progress";
                    lastResult = ArrayUtils.add(controlSystemHelper.initDevices(false, in), 0, getExecutionDate());
                } catch (final DevFailed e) {
                    lastResult = new String[] { getExecutionDate(), DevFailedUtils.toString(e) };
                    DevFailedUtils.logDevFailed(e, logger);
                } finally {
                    state = DeviceState.ON;
                    status = WAITING_FOR_REQUEST;
                }

            }
        }).start();
    }

    /**
     * Execute a command on a group of devices
     *
     * @param in
     *            The device pattern (wildcard char is *),command name, timeout
     *            (optional)
     * @throws DevFailed
     */
    @Command(inTypeDesc = "The device pattern (wildcard char is *) on which command will be executed,command name, timeout(optional)", displayLevel = DispLevel._EXPERT)
    @StateMachine(deniedStates = DeviceState.INIT)
    public void commandDevices(final String[] in) throws DevFailed {
        final String className = in[0];
        final String commandName = in[1];
        final int timeout = controlSystemHelper.getTimeout(in);
        final String[] devices = controlSystemHelper.getExportedDevicesForClass(className);
        logger.debug("command {} on devices {}", commandName, Arrays.toString(devices));
        controlSystemHelper.groupedCommandForget(timeout, commandName, devices);
    }

    /**
     * Get state of devices and report result in lastStateResult attribute
     *
     * @param in
     *            The device pattern (wildcard char is *), timeout (optional)
     * @return
     * @throws DevFailed
     */
    @Command(inTypeDesc = DESC_1, outTypeDesc = "The state of all class devices")
    @StateMachine(deniedStates = DeviceState.INIT)
    public void getDevicesState(final String deviceName) throws DevFailed {
        // detach execution and log result in an attribute
        new Thread(new Runnable() {

            @Override
            public void run() {
                try {
                    state = DeviceState.RUNNING;
                    status = "Retrieving state of " + deviceName;
                    lastResult = ArrayUtils.add(controlSystemHelper.getDevicesState(deviceName), 0, getExecutionDate());
                } catch (final DevFailed e) {
                    lastResult = new String[] { getExecutionDate(), DevFailedUtils.toString(e) };
                    logger.error("Failed to get state {}", DevFailedUtils.toString(e));
                } finally {
                    state = DeviceState.ON;
                    status = WAITING_FOR_REQUEST;
                }
            }
        }).start();
    }

    /**
     * Get state of devices
     *
     * @param in
     *            The device pattern (wildcard char is *), timeout (optional)
     * @return
     * @throws DevFailed
     */
    @Command(inTypeDesc = DESC_1, outTypeDesc = "The state of all class devices", displayLevel = DispLevel._EXPERT)
    @StateMachine(deniedStates = DeviceState.INIT)
    public String[] getDevicesStateSync(final String[] in) throws DevFailed {
        return controlSystemHelper.getDevicesState(in);
    }

    /**
     * Get status of devices
     *
     * @param in
     *            The device pattern (wildcard char is *), timeout (optional)
     * @return
     * @throws DevFailed
     */
    @Command(inTypeDesc = "the device pattern", outTypeDesc = "The status of all class devices")
    @StateMachine(deniedStates = { DeviceState.INIT, DeviceState.RUNNING })
    public void getDevicesStatus(final String devicePattern) throws DevFailed {
        // detach execution and log result in an attribute
        new Thread(new Runnable() {

            @Override
            public void run() {
                try {
                    state = DeviceState.RUNNING;
                    status = "Retrieving status of " + devicePattern;

                    lastResult = ArrayUtils.add(controlSystemHelper.getDevicesStatus(devicePattern), 0,
                            getExecutionDate());

                } catch (final DevFailed e) {
                    lastResult = new String[] { getExecutionDate(), DevFailedUtils.toString(e) };
                    logger.error("Failed to get status {}", DevFailedUtils.toString(e));
                } finally {
                    state = DeviceState.ON;
                    status = WAITING_FOR_REQUEST;
                }
            }
        }).start();
    }

    /**
     * Get status of devices
     *
     * @param in
     *            The device pattern (wildcard char is *), timeout (optional)
     * @return
     * @throws DevFailed
     */
    @Command(inTypeDesc = DESC_1, outTypeDesc = "The status of all class devices", displayLevel = DispLevel._EXPERT)
    @StateMachine(deniedStates = DeviceState.INIT)
    public String[] getDevicesStatusSync(final String[] in) throws DevFailed {
        return controlSystemHelper.getDevicesStatus(in);
    }

    /**
     * Ping a group of devices
     *
     * @param in
     *            The device pattern (wildcard char is *), timeout (optional)
     * @return
     * @throws DevFailed
     */
    @Command(inTypeDesc = DESC_1, outTypeDesc = "true if all devices are alive", displayLevel = DispLevel._EXPERT)
    @StateMachine(deniedStates = DeviceState.INIT)
    public boolean pingDevicesSync(final String[] in) throws DevFailed {
        final String devicePattern = in[0];
        int timeout = DEFAULT_TIMEOUT;
        if (in.length > 1) {
            timeout = Integer.parseInt(in[1]);
        }
        final String[] devices = controlSystemHelper.getDevices(devicePattern);
        logger.debug("ping devices {}", Arrays.toString(devices));
        return controlSystemHelper.createGroup(devices, timeout).ping(true);
    }

    /**
     * Ping a group of devices
     *
     * @param in
     *            The device class pattern (wildcard char is *), timeout
     *            (optional)
     * @return
     * @throws DevFailed
     */
    @Command(inTypeDesc = DESC_2, outTypeDesc = "true if all devices are alive")
    @StateMachine(deniedStates = { DeviceState.INIT, DeviceState.RUNNING })
    public void pingDevices(final String in) throws DevFailed {
        // detach execution and log result in an attribute
        new Thread(new Runnable() {

            @Override
            public void run() {
                try {
                    state = DeviceState.RUNNING;
                    status = "ping of " + in;
                    final String[] devices = controlSystemHelper.getDevices(in);
                    logger.debug("ping devices {}", Arrays.toString(devices));
                    final boolean hasPing = controlSystemHelper.createGroup(devices, 3000).ping(true);
                    lastResult = new String[] { getExecutionDate(), Boolean.toString(hasPing) };
                } catch (final DevFailed e) {
                    lastResult = new String[] { getExecutionDate(), DevFailedUtils.toString(e) };
                    logger.error("Failed to get status {}", DevFailedUtils.toString(e));
                } finally {
                    state = DeviceState.ON;
                    status = WAITING_FOR_REQUEST;
                }
            }
        }).start();
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(final String status) {
        this.status = status;
    }

    public DeviceState getState() {
        return state;
    }

    public void setState(final DeviceState state) {
        this.state = state;
    }

    public void setDynamicManager(final DynamicManager dynamicManager) {
        this.dynamicManager = dynamicManager;
    }

    public String[] getLastResult() {
        return lastResult;
    }

}

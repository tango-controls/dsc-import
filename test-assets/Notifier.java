/**
 * 
 */
package fr.soleil.tango.server.notifier;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.tango.DeviceState;
import org.tango.server.ServerManager;
import org.tango.server.annotation.Command;
import org.tango.server.annotation.Delete;
import org.tango.server.annotation.Device;
import org.tango.server.annotation.DeviceProperty;
import org.tango.server.annotation.DynamicManagement;
import org.tango.server.annotation.Init;
import org.tango.server.annotation.StateMachine;
import org.tango.server.annotation.TransactionType;
import org.tango.server.attribute.log.LogAttribute;
import org.tango.server.dynamic.DynamicManager;
import org.tango.utils.DevFailedUtils;

import fr.esrf.Tango.DevFailed;
import fr.esrf.TangoApi.Database;
import fr.esrf.TangoApi.DbDatum;

import fr.soleil.notification.EMailNotification;
import fr.soleil.notification.NotificationException;
import fr.soleil.notification.TextTalkerNotification;

/**
 * @author ABEILLE
 * 
 */
@Device(transactionType = TransactionType.NONE)
public class Notifier {

    public static final String LOGGER_NAME = "Notification";
    private final static Logger logger = LoggerFactory.getLogger(LOGGER_NAME);
    private EMailNotification notificationSender = new EMailNotification();

    private TextTalkerNotification texttalker;

    @DynamicManagement
    DynamicManager dynamicManager;

    @DeviceProperty(defaultValue = "tango@synchrotron-soleil.fr")
    String eMailEmitter = "";

    public void setEMailEmitter(final String eMailEmitter) {
        this.eMailEmitter = eMailEmitter;
    }

    public void setEMailServer(final String eMailServer) {
        this.eMailServer = eMailServer;
    }

    @DeviceProperty(defaultValue = "sun-owa.synchrotron-soleil.fr")
    String eMailServer = "";

    @Init
    @StateMachine(endState = DeviceState.ON)
    public void init() throws DevFailed {
        dynamicManager.addAttribute(new LogAttribute(1000, logger));
        notificationSender = new EMailNotification(eMailServer);
        notificationSender.setEmitter(eMailEmitter);

        logger.info("e-mail notification with server {} and emitter {}", eMailServer, eMailEmitter);
    }

    private TextTalkerNotification getTextalkerNotifier() throws DevFailed {
        if (texttalker == null) {
            String texttalkerDevice = getClassProperty("TexttalkerDevice");
            if (texttalkerDevice == null) {
                DevFailedUtils.throwDevFailed("TexttalkerDevice property in Notifier device is not initialized.");
            }
            List<String> list = new ArrayList<String>();
            list.add(texttalkerDevice);
            try {
                texttalker = new TextTalkerNotification(list);
            } catch (NotificationException e) {
                DevFailedUtils.throwDevFailed(e);
            }
        }

        return texttalker;
    }

    @Delete
    public void delete() throws DevFailed {
        dynamicManager.clearAll();
    }

    public static String getFirstNotifier() throws DevFailed {
        return ServerManager.getInstance().getDevicesOfClass(Notifier.class.getSimpleName())[0];
    }

    public static String getClassProperty(final String classPropertyName) {
        // Get the name of the manager device

        String className;
        String deviceName = null;
        String propValue = null;

        try {
            Database database = new Database();
            String[] deviceList = database.get_device_exported_for_class("Notifier");
            if ((deviceList != null) && (deviceList.length > 0)) {
                deviceName = deviceList[0];

                if (database != null) {
                    DbDatum dbDatum = database.get_device_property(deviceName, classPropertyName);
                    if ((dbDatum != null) && !dbDatum.is_empty()) {
                        propValue = dbDatum.extractString();

                    }
                }

            } else {
                DevFailedUtils.throwDevFailed("Notifier doesn't find.");
            }

        } catch (DevFailed devFailed) {
            DevFailedUtils.logDevFailed(devFailed, logger);
        }

        return propValue;
    }

    /**
     * @param args
     */
    public static void main(final String[] args) {
        ServerManager.getInstance().addClass(Notifier.class.getSimpleName(), Notifier.class);
        // ServerManager.getInstance().addClass(EventMonitor.class.getSimpleName(), EventMonitor.class);
        ServerManager.getInstance().start(args, Notifier.class.getSimpleName());
    }

    @Command(inTypeDesc = "String subject,  String message, String[] addresses")
    public void sendEmail(final String[] in) throws DevFailed {
        if (in.length < 3) {
            DevFailedUtils.throwDevFailed("input parameter must be at least of size 3");
        }

        notificationSender.setSubject(in[0]);
        notificationSender.setMessage(in[1]);
        final String[] recipients = Arrays.copyOfRange(in, 2, in.length);
        notificationSender.setRecipient(recipients);
        try {
            notificationSender.emit();
        } catch (NotificationException ex) {
            DevFailedUtils.throwDevFailed(ex);
        }
    }

    @Command(inTypeDesc = "String message")
    public void sendTexttalker(final String[] in) throws DevFailed {
        if (in.length > 1) {
            DevFailedUtils.throwDevFailed("input parameter must be of size 1");
        }
        TextTalkerNotification texttalkerTmp = getTextalkerNotifier();
        texttalkerTmp.setMessage(in[0]);

        try {
            texttalkerTmp.emit();
        } catch (NotificationException ex) {
            DevFailedUtils.throwDevFailed(ex);
        }
    }

    public void setDynamicManager(final DynamicManager dynamicManager) {
        this.dynamicManager = dynamicManager;
    }

}
